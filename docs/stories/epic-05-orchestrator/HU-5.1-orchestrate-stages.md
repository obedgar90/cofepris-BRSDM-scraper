# HU-5.1 — Orchestrate scraper, transform, and load

- **Epic**: 05 Orchestrator
- **Status**: done
- **Owner**: @team
- **Created**: 2026-05-13
- **Last update**: 2026-05-13

## Story
As an operator, I want one orchestrator entrypoint to run stages in order so that the pipeline is deterministic.

## Acceptance criteria
- [x] Executes download, normalize, and load in order.
- [x] Returns timing and row metrics.
- [x] Cleans temporary downloaded file.

## Tests (written first, TDD red phase)
- `tests/unit/pipeline/test_orchestrator.py`
