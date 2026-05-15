"""Proxy selection strategy with persisted health and circuit states."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import DateTime, Integer, MetaData, String, Table, and_, delete, insert, select
from sqlalchemy.engine import Engine
from sqlalchemy.sql.schema import Column


class ProxyStrategy:
    """Select proxy endpoints using health scoring and circuit-breaker semantics."""

    def __init__(
        self,
        engine: Engine,
        proxy_servers: tuple[str, ...],
        proxy_username: str | None = None,
        proxy_password: str | None = None,
        circuit_failure_threshold: int = 3,
        circuit_cooldown_seconds: int = 600,
        half_open_max_trials: int = 1,
        sticky_ttl_seconds: int = 900,
        health_decay_on_success: int = 1,
        health_penalty_timeout: int = 1,
        health_penalty_block: int = 3,
        fail_open: bool = True,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self._engine = engine
        self._proxy_servers = proxy_servers
        self._proxy_username = proxy_username
        self._proxy_password = proxy_password
        self._circuit_failure_threshold = circuit_failure_threshold
        self._circuit_cooldown_seconds = circuit_cooldown_seconds
        self._half_open_max_trials = half_open_max_trials
        self._sticky_ttl_seconds = sticky_ttl_seconds
        self._health_decay_on_success = health_decay_on_success
        self._health_penalty_timeout = health_penalty_timeout
        self._health_penalty_block = health_penalty_block
        self._fail_open = fail_open
        self._now_provider = now_provider or (lambda: datetime.now(tz=UTC))
        self._fallback_index = 0

        metadata = MetaData()
        self._state_table = Table(
            "proxy_runtime_state",
            metadata,
            Column("proxy_server", String(512), primary_key=True),
            Column("domain", String(255), primary_key=True),
            Column("state", String(20), nullable=False),
            Column("failure_count", Integer, nullable=False),
            Column("success_count", Integer, nullable=False),
            Column("ban_score", Integer, nullable=False),
            Column("opened_at", DateTime(timezone=True), nullable=True),
            Column("cooldown_until", DateTime(timezone=True), nullable=True),
            Column("last_used_at", DateTime(timezone=True), nullable=True),
            Column("sticky_session_id", String(255), nullable=True),
            Column("updated_at", DateTime(timezone=True), nullable=False),
            Column("half_open_trial_count", Integer, nullable=False),
        )
        metadata.create_all(self._engine)

    def select_proxy(self, domain: str) -> dict[str, str]:
        """Return one proxy configuration payload for Playwright."""
        if not self._proxy_servers:
            raise RuntimeError("No proxy servers configured for strategy.")
        try:
            now = self._now_provider()
            states = self._load_states_for_domain(domain)
            candidates: list[dict[str, Any]] = []
            for proxy_server in self._proxy_servers:
                state = states.get(proxy_server, self._default_state(domain, proxy_server))
                proxy_state = state["state"]
                if proxy_state == "open":
                    cooldown_until = self._as_utc_datetime(state["cooldown_until"])
                    if cooldown_until is None or cooldown_until > now:
                        continue
                    state["state"] = "half_open"
                    state["half_open_trial_count"] = 0
                    self._upsert_state(state)
                    proxy_state = "half_open"
                if (
                    proxy_state == "half_open"
                    and state["half_open_trial_count"] >= self._half_open_max_trials
                ):
                    continue
                candidates.append(state)
            sticky_candidate = self._pick_sticky_candidate(candidates, now)
            selected = sticky_candidate or self._rank_candidates(candidates)[0]
            selected["last_used_at"] = now
            selected["sticky_session_id"] = selected["proxy_server"]
            if selected["state"] == "half_open":
                selected["half_open_trial_count"] += 1
            self._upsert_state(selected)
            return self._build_proxy_payload(selected["proxy_server"])
        except Exception:
            if self._fail_open:
                return self._fallback_round_robin()
            raise

    def report_outcome(self, *, domain: str, proxy_server: str, outcome: str) -> None:
        """Update persisted proxy health after one attempt outcome."""
        try:
            state = self._get_or_create_state(domain=domain, proxy_server=proxy_server)
            now = self._now_provider()
            state["updated_at"] = now
            if outcome == "success":
                state["success_count"] += 1
                state["failure_count"] = 0
                state["ban_score"] = max(0, state["ban_score"] - self._health_decay_on_success)
                state["state"] = "closed"
                state["opened_at"] = None
                state["cooldown_until"] = None
                state["half_open_trial_count"] = 0
            elif outcome == "transient_failure":
                self._apply_failure(state, now, self._health_penalty_timeout)
            elif outcome == "bot_blocked":
                self._apply_failure(state, now, self._health_penalty_block)
            elif outcome == "ui_changed":
                pass
            self._upsert_state(state)
        except Exception:
            if not self._fail_open:
                raise

    def get_state(self, *, domain: str, proxy_server: str) -> dict[str, Any]:
        """Expose one state row for unit tests."""
        return dict(self._get_or_create_state(domain=domain, proxy_server=proxy_server))

    def _apply_failure(self, state: dict[str, Any], now: datetime, penalty: int) -> None:
        state["failure_count"] += 1
        state["ban_score"] += penalty
        must_open = state["failure_count"] >= self._circuit_failure_threshold
        failed_half_open_probe = state["state"] == "half_open"
        if must_open or failed_half_open_probe:
            state["state"] = "open"
            state["opened_at"] = now
            state["cooldown_until"] = now + timedelta(seconds=self._circuit_cooldown_seconds)
            state["half_open_trial_count"] = 0

    def _pick_sticky_candidate(
        self, candidates: list[dict[str, Any]], now: datetime
    ) -> dict[str, Any] | None:
        sticky_threshold = now - timedelta(seconds=self._sticky_ttl_seconds)
        sticky = [
            row
            for row in candidates
            if row["state"] == "closed"
            and self._as_utc_datetime(row["last_used_at"]) is not None
            and self._as_utc_datetime(row["last_used_at"]) >= sticky_threshold
        ]
        if not sticky:
            return None
        return sorted(
            sticky,
            key=lambda row: self._as_utc_datetime(row["last_used_at"]),
            reverse=True,
        )[0]

    def _rank_candidates(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not candidates:
            raise RuntimeError("No healthy proxy candidate available.")
        state_rank = {"closed": 0, "half_open": 1, "open": 2}
        distant_past = datetime(1970, 1, 1, tzinfo=UTC)
        return sorted(
            candidates,
            key=lambda row: (
                state_rank.get(row["state"], 99),
                row["ban_score"],
                self._as_utc_datetime(row["last_used_at"]) or distant_past,
                row["proxy_server"],
            ),
        )

    def _fallback_round_robin(self) -> dict[str, str]:
        proxy_server = self._proxy_servers[self._fallback_index % len(self._proxy_servers)]
        self._fallback_index += 1
        return self._build_proxy_payload(proxy_server)

    def _build_proxy_payload(self, proxy_server: str) -> dict[str, str]:
        payload = {"server": proxy_server}
        if self._proxy_username is not None:
            payload["username"] = self._proxy_username
        if self._proxy_password is not None:
            payload["password"] = self._proxy_password
        return payload

    def _load_states_for_domain(self, domain: str) -> dict[str, dict[str, Any]]:
        statement = select(self._state_table).where(self._state_table.c.domain == domain)
        with self._engine.connect() as connection:
            rows = connection.execute(statement).mappings().all()
        return {row["proxy_server"]: dict(row) for row in rows}

    def _get_or_create_state(self, *, domain: str, proxy_server: str) -> dict[str, Any]:
        where_clause = and_(
            self._state_table.c.proxy_server == proxy_server,
            self._state_table.c.domain == domain,
        )
        statement = select(self._state_table).where(where_clause)
        with self._engine.connect() as connection:
            row = connection.execute(statement).mappings().first()
        if row:
            return dict(row)
        state = self._default_state(domain=domain, proxy_server=proxy_server)
        self._upsert_state(state)
        return state

    def _default_state(self, domain: str, proxy_server: str) -> dict[str, Any]:
        now = self._now_provider()
        return {
            "proxy_server": proxy_server,
            "domain": domain,
            "state": "closed",
            "failure_count": 0,
            "success_count": 0,
            "ban_score": 0,
            "opened_at": None,
            "cooldown_until": None,
            "last_used_at": None,
            "sticky_session_id": None,
            "updated_at": now,
            "half_open_trial_count": 0,
        }

    def _upsert_state(self, state: dict[str, Any]) -> None:
        where_clause = and_(
            self._state_table.c.proxy_server == state["proxy_server"],
            self._state_table.c.domain == state["domain"],
        )
        with self._engine.begin() as connection:
            connection.execute(delete(self._state_table).where(where_clause))
            connection.execute(insert(self._state_table).values(**state))

    @staticmethod
    def _as_utc_datetime(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
