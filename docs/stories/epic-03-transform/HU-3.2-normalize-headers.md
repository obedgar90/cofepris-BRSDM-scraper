# HU-3.2 — Normalize headers to snake_case ASCII

- **Epic**: 03 Transform
- **Status**: done
- **Owner**: @team
- **Created**: 2026-05-13
- **Last update**: 2026-05-13

## Story
As a pipeline component, I want normalized snake_case ASCII headers so that PostgreSQL column names are stable and compatible.

## Acceptance criteria
- [x] Removes accents and special symbols.
- [x] Produces deterministic lowercase snake_case.

## Tests (written first, TDD red phase)
- `tests/unit/transform/test_normalizer.py::test_normalize_header_removes_accents_symbols_and_uses_snake_case`
