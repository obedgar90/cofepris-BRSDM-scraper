# HU-3.1 — Read Excel dataset

- **Epic**: 03 Transform
- **Status**: done
- **Owner**: @team
- **Created**: 2026-05-13
- **Last update**: 2026-05-13

## Story
As a pipeline component, I want to read the downloaded Excel file into a DataFrame so that downstream stages can process it.

## Acceptance criteria
- [x] Reads sample file from `info/`.
- [x] Produces a non-empty DataFrame with required columns.

## Tests (written first, TDD red phase)
- `tests/unit/transform/test_normalizer.py::test_normalize_reads_sample_excel_and_returns_29_columns`
