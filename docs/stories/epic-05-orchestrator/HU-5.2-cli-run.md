# HU-5.2 — CLI one-shot run command

- **Epic**: 05 Orchestrator
- **Status**: done
- **Owner**: @team
- **Created**: 2026-05-13
- **Last update**: 2026-05-13

## Story
As an operator, I want a one-shot CLI command so that the pipeline can run from cron jobs and CI tasks.

## Acceptance criteria
- [x] `cofepris run` executes pipeline and prints JSON result.
- [x] Known failures map to stage-specific exit codes.

## Tests (written first, TDD red phase)
- `tests/unit/cli/test_cli.py`
