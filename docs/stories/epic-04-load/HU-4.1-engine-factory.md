# HU-4.1 — Engine factory from settings

- **Epic**: 04 Load
- **Status**: done
- **Owner**: @team
- **Created**: 2026-05-13
- **Last update**: 2026-05-13

## Story
As a load layer component, I want SQLAlchemy engine creation isolated so that database connectivity is configurable and testable.

## Acceptance criteria
- [x] Engine creation is encapsulated in `EngineFactory`.

## Tests (written first, TDD red phase)
- `tests/unit/load/test_engine_factory.py`
