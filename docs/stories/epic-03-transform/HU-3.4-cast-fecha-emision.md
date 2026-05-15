# HU-3.4 — Cast fecha_emision to datetime

- **Epic**: 03 Transform
- **Status**: done
- **Owner**: @team
- **Created**: 2026-05-13
- **Last update**: 2026-05-13

## Story
As an analyst, I want `fecha_emision` typed as datetime so that date-based analysis is reliable.

## Acceptance criteria
- [x] `fecha_emision` is parsed as datetime.

## Tests (written first, TDD red phase)
- `tests/unit/transform/test_normalizer.py::test_normalize_casts_fecha_emision_to_datetime`
