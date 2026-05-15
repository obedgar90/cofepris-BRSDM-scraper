# HU-2.4 — Retry and backoff for downloads

- **Epic**: 02 Scraper
- **Status**: done
- **Owner**: @team
- **Created**: 2026-05-13
- **Last update**: 2026-05-13

## Story
As an operator, I want transient download failures retried with backoff so that temporary portal issues do not fail the whole run.

## Acceptance criteria
- [x] Timeout failures are retried.
- [x] UI drift errors fail fast.
- [x] Retries stop with `DownloadError` after exhaustion.

## Tests (written first, TDD red phase)
- `tests/unit/scraper/test_downloader.py`
