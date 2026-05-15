"""Proxy strategy V2 unit tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine

from cofepris_brsdm_scraper.scraper.proxy_strategy import ProxyStrategy


def test_proxy_strategy_selects_sticky_healthy_proxy_for_domain() -> None:
    """Strategy should keep sticky proxy for the same domain when healthy."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    strategy = ProxyStrategy(
        engine=engine,
        proxy_servers=("http://proxy-a:8080", "http://proxy-b:8080"),
        sticky_ttl_seconds=300,
    )
    domain = "tramiteselectronicos02.cofepris.gob.mx"

    first_proxy = strategy.select_proxy(domain)
    strategy.report_outcome(domain=domain, proxy_server=first_proxy["server"], outcome="success")

    second_proxy = strategy.select_proxy(domain)

    assert second_proxy["server"] == first_proxy["server"]
    engine.dispose()


def test_proxy_strategy_opens_circuit_after_threshold_failures() -> None:
    """Strategy should open circuit for failing proxy and pick another proxy."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    strategy = ProxyStrategy(
        engine=engine,
        proxy_servers=("http://proxy-a:8080", "http://proxy-b:8080"),
        circuit_failure_threshold=2,
        circuit_cooldown_seconds=60,
        health_penalty_timeout=1,
    )
    domain = "tramiteselectronicos02.cofepris.gob.mx"

    strategy.report_outcome(
        domain=domain,
        proxy_server="http://proxy-a:8080",
        outcome="transient_failure",
    )
    strategy.report_outcome(
        domain=domain,
        proxy_server="http://proxy-a:8080",
        outcome="transient_failure",
    )

    selected = strategy.select_proxy(domain)

    assert selected["server"] == "http://proxy-b:8080"
    engine.dispose()


def test_proxy_strategy_moves_open_proxy_to_half_open_after_cooldown() -> None:
    """Proxy circuit should transition to half-open when cooldown expires."""
    now = datetime(2026, 5, 13, 23, 0, tzinfo=UTC)
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    strategy = ProxyStrategy(
        engine=engine,
        proxy_servers=("http://proxy-a:8080",),
        circuit_failure_threshold=1,
        circuit_cooldown_seconds=30,
        now_provider=lambda: now,
    )
    domain = "tramiteselectronicos02.cofepris.gob.mx"

    strategy.report_outcome(
        domain=domain,
        proxy_server="http://proxy-a:8080",
        outcome="bot_blocked",
    )
    strategy._now_provider = lambda: now + timedelta(seconds=31)

    selected = strategy.select_proxy(domain)
    state = strategy.get_state(domain=domain, proxy_server="http://proxy-a:8080")

    assert selected["server"] == "http://proxy-a:8080"
    assert state["state"] == "half_open"
    engine.dispose()


def test_proxy_strategy_fail_open_returns_round_robin_when_store_fails() -> None:
    """Strategy should degrade gracefully when persistence layer fails."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    strategy = ProxyStrategy(
        engine=engine,
        proxy_servers=("http://proxy-a:8080", "http://proxy-b:8080"),
        fail_open=True,
    )
    domain = "tramiteselectronicos02.cofepris.gob.mx"

    strategy._load_states_for_domain = lambda _: (_ for _ in ()).throw(RuntimeError("db down"))

    selected_first = strategy.select_proxy(domain)
    selected_second = strategy.select_proxy(domain)

    assert selected_first["server"] == "http://proxy-a:8080"
    assert selected_second["server"] == "http://proxy-b:8080"
    engine.dispose()
