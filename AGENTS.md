# AGENTS.md - agents (this collection)

This repository holds `AGENTS.md` templates by stack plus the core docs and
validator. Markdown and one Python script; no build. The seven articles of
`CONSTITUTION.md` apply to the templates it ships and to edits here.

## Commands

- Check (the CI gate): `python3 tools/check_templates.py` - validates every `stacks/*/AGENTS.md` and its companions; exit 1 on any error.
- No other build or test step exists. CI runs the same command (`.github/workflows/check.yml`).

## Architecture

- `CONSTITUTION.md` is the source of the fixed practices; `core/` explains and cites them; `stacks/<stack>/` instantiates them per stack; `tools/check_templates.py` enforces the writing rules in `core/writing-agent-files.md`.
- A stack folder is always: `AGENTS.md`, `CLAUDE.md` containing `@AGENTS.md`, `.github/copilot-instructions.md`, `agent_docs/{architecture,testing,observability,gates}.md`, `README.md`.
- Evidence for a rule is a record slug in `core/evidence.md`; the records live in the research corpus outside this repo.

## Testing

- Every change to a template or to `core/` runs `python3 tools/check_templates.py` and passes with zero errors before commit.
- A new validator rule ships with a stack file that would fail it, fixed in the same change.

## Observability

- Not applicable to a docs repository; the templates carry the rules for real projects.

## Boundaries

- Always: keep every `stacks/*/AGENTS.md` under 150 lines; make every directive name a path, command, tool or number; add the evidence slug in `core/evidence.md` when you add a rule to `core/`.
- Ask first: adding a stack; changing `CONSTITUTION.md` (needs a version bump and a reason); changing the budgets in `tools/check_templates.py`.
- Never: add style or formatting rules to a template (they go in the stack's linter config, see `core/writing-agent-files.md`); add a persona line ("you are a senior engineer") anywhere; use em-dashes or arrows in prose (use `-` and `=>`, the validator rejects them); leave `TODO` or `TBD` in a template.

## Where to look

- `core/writing-agent-files.md` - the budget, anatomy and directive rule the validator enforces
- `docs/specs/2026-09-08-template-collection.md` - the decisions and open questions
- `stacks/kotlin-android/` - the reference stack; copy its shape for a new one
