# Cursor Project Rules

This folder contains persistent guidance for AI agents in Cursor.

## Structure

- `rules/00-project-governance.mdc`: global safety, scope, and SOLID guardrails.
- `rules/10-python-implementation.mdc`: Python implementation standards.
- `rules/20-tests-tdd.mdc`: pytest-oriented TDD workflow.
- `rules/30-docs-and-agent-guidance.mdc`: documentation language and AGENTS consistency.

## Maintenance

- Keep each rule focused on one concern.
- Prefer updating existing rules over creating overlapping ones.
- If project conventions change, update `AGENTS.md` and matching `.mdc` rules together.
