# HU-6.1 — Daemon mode with cron schedule

- **Epic**: 06 Scheduler
- **Status**: done
- **Owner**: @team
- **Created**: 2026-05-13
- **Last update**: 2026-05-13

## Story
As an operator, I want daemon mode with cron scheduling so that the pipeline runs periodically without external orchestration.

## Acceptance criteria
- [x] Supports 5-field cron expression.
- [x] Uses lock file to prevent overlapping runs.
