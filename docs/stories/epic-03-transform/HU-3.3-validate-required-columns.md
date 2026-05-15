# HU-3.3 — Validate required columns

- **Epic**: 03 Transform
- **Status**: done
- **Owner**: @team
- **Created**: 2026-05-13
- **Last update**: 2026-05-13

## Story
As a pipeline component, I want to fail fast when required columns are missing so that portal drift is detected immediately.

## Acceptance criteria
- [x] Raises `MissingColumnError` when any required column is absent.

## Tests (written first, TDD red phase)
- `tests/unit/transform/test_normalizer.py::test_normalize_raises_missing_column_error_when_required_column_absent`
