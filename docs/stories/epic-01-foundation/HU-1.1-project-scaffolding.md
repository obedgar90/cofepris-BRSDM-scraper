# HU-1.1 — Project scaffolding and tooling

- **Epic**: 01 Foundation
- **Status**: done
- **Owner**: @team
- **Created**: 2026-05-13
- **Last update**: 2026-05-13

## Story
As a maintainer, I want a reproducible Python project scaffold so that contributors can run tests and quality checks consistently.

## Acceptance criteria
- [x] `pyproject.toml` defines runtime and dev dependencies.
- [x] `pytest`, `ruff`, and `mypy` are configured.

## Tests (written first, TDD red phase)
- `tests/unit/config/test_settings.py`
- `tests/unit/load/test_engine_factory.py`
