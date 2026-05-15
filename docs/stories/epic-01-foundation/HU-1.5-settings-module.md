# HU-1.5 — Typed settings module

- **Epic**: 01 Foundation
- **Status**: done
- **Owner**: @team
- **Created**: 2026-05-13
- **Last update**: 2026-05-13

## Story
As a maintainer, I want typed settings loaded from environment variables so that secrets and runtime values are not hardcoded.

## Acceptance criteria
- [x] `Settings` reads `.env` and environment variables.
- [x] Missing `DATABASE_URL` raises validation error.

## Tests (written first, TDD red phase)
- `tests/unit/config/test_settings.py::test_settings_raise_validation_error_when_database_url_missing`
