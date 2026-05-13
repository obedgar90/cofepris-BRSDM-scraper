# AGENTS.md

Project-level instructions for AI coding agents working on `cofepris-BRSDM-scraper`.

## Mission

Build and maintain a reliable pipeline that:

- Downloads the "COMPLETO" medicines registry Excel file from COFEPRIS using Playwright (Chromium, headless).
- Normalizes column names and dataset shape with pandas.
- Loads the normalized data into PostgreSQL through SQLAlchemy.

## Core Principles (Always)

- Apply SOLID principles in architecture and implementation.
- Use TDD: write or update failing tests first, then implement, then make tests pass.
- Keep changes small, focused, and reversible.
- Preserve backward compatibility unless explicitly asked to break it.
- Prefer explicit error handling, retries, and clear logs over silent failures.

## Language and Documentation Requirements

- Write all new documentation in English.
- Write all tests in English (test names, docstrings, comments, fixture descriptions).
- Keep user-facing and operational instructions concise and actionable.

## Tech Stack and Expected Tooling

- Language: Python.
- Scraping: Playwright + Chromium.
- Data processing: pandas.
- Database I/O: SQLAlchemy + PostgreSQL.
- Tests: pytest.
- Runtime and orchestration: Docker Compose.

If the repo does not yet contain full scaffolding (for example, missing `docker-compose.yml` or test layout), propose and implement minimal structure incrementally via TDD.

## Safety and Permission Boundaries

Allowed without extra confirmation:

- Read files, inspect project structure, run focused tests and lint checks.
- Add or update code/tests/docs needed for the requested task.

Ask before:

- Adding new dependencies.
- Changing database schema or destructive data operations.
- Running full end-to-end scraping against production endpoints repeatedly.
- Editing CI/CD, release, secrets, or infrastructure settings.

Never:

- Commit secrets, tokens, or credentials.
- Disable tests to make builds pass.
- Introduce destructive commands against Git or data stores without explicit user approval.

## Development Workflow (Mandatory)

1. Understand the requested behavior and affected modules.
2. Write or update tests first (unit tests by default, integration only when necessary).
3. Run tests and confirm they fail for the expected reason.
4. Implement the minimal code to pass tests.
5. Refactor while keeping tests green.
6. Run relevant quality checks.
7. Update documentation when behavior or operations change.

## Project Structure Guidance

When creating or extending code, prefer this structure:

- `src/scraper/` for Playwright navigation and download logic.
- `src/transform/` for pandas normalization and schema mapping.
- `src/load/` for SQLAlchemy ingestion and transactional writes.
- `src/pipeline/` for orchestration/use-case services.
- `tests/unit/` for isolated behavior tests.
- `tests/integration/` for DB and end-to-end pipeline integration tests.
- `info/` for sample input artifacts (already present in this repo).

## Data Handling Rules

- Normalize headers to snake_case ASCII (remove accents and special characters).
- Keep a deterministic mapping strategy for source column names.
- Validate required columns before transformation and before DB load.
- Handle large files with chunked inserts when relevant.
- Make idempotency explicit (for example, replace vs append strategy) and test it.

## Scraper Robustness Rules

- Use stable selectors and encapsulate selector definitions in one place.
- Add retry/backoff for transient portal failures.
- Detect portal/UI changes early and fail with actionable error messages.
- Avoid hardcoding brittle waits; prefer explicit waits for page states/events.

## Quality Gates Before Finishing

- Relevant tests pass locally.
- New code is covered by tests for expected behavior and at least one failure path.
- Documentation reflects operational or behavioral changes.
- No credentials or sensitive paths are introduced.

## When Stuck

- Do not guess hidden requirements.
- State assumptions explicitly.
- Propose the smallest safe next step and ask focused clarification questions.
