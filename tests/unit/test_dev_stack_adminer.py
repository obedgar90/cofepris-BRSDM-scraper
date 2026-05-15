"""Tests for local dev stack database UI setup."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _read_text(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_compose_makefile_and_readme_reference_adminer_ui() -> None:
    """Local stack should expose Adminer and document how to use it."""
    compose = _read_text("docker-compose.yml")
    makefile = _read_text("Makefile")
    readme = _read_text("README.md")

    assert "adminer:" in compose
    assert "8080:8080" in compose
    assert "condition: service_healthy" in compose
    assert "adminer" in makefile
    assert "db-ui-up:" in makefile
    assert "db-up-down:" in makefile
    assert "http://localhost:8080" in readme
    assert "server: `postgres`" in readme
