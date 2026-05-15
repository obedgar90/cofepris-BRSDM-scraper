# HU-8.5 — Story docs checker script

- **Epic**: 08 Docs
- **Status**: done
- **Owner**: @team
- **Created**: 2026-05-13
- **Last update**: 2026-05-13

## Story
As a maintainer, I want an automated checker that validates story doc coverage so that project governance remains enforceable.

## Acceptance criteria
- [x] `scripts/check_story_docs.py` validates plan HU entries against docs.
- [x] Hook is wired into `.pre-commit-config.yaml`.
