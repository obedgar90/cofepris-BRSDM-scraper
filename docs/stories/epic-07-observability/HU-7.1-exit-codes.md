# HU-7.1 — Stage-specific exit codes

- **Epic**: 07 Observability
- **Status**: done
- **Owner**: @team
- **Created**: 2026-05-13
- **Last update**: 2026-05-13

## Story
As an operator, I want explicit exit codes by stage so that alerting and automation can route failures correctly.

## Acceptance criteria
- [x] Download failures return exit code 10.
- [x] Transform failures return exit code 20.
- [x] Load failures return exit code 30.
- [x] Generic pipeline failures return exit code 40.
