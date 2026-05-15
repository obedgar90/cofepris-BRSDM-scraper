# HU-4.2 — Replace load with transactional swap

- **Epic**: 04 Load
- **Status**: done
- **Owner**: @team
- **Created**: 2026-05-13
- **Last update**: 2026-05-13

## Story
As a pipeline component, I want replace-mode loading with staging swap so that each run produces a clean snapshot safely.

## Acceptance criteria
- [x] Uses staging table and swap strategy.
- [x] Creates unique index for `numero_de_registro`.
- [x] Wraps DB failures as `DatabaseUnavailableError`.

## Tests (written first, TDD red phase)
- `tests/unit/load/test_postgres_loader.py`
