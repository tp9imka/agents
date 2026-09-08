# python template

Copy `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` and
`agent_docs/` into the repository root, then:

1. Replace `<Project>`, `<project>`, `<3.1x>`, the framework choices (FastAPI/Django) and the exemplar paths with real files.
2. Ship the gates the file names: `Makefile` with `check`, `pyproject.toml`
   tool sections (ruff with `banned-api`, mypy strict, pytest and coverage
   with `fail_under = 100`), `.importlinter`, `.pre-commit-config.yaml`, the
   `check.yml` / `nightly.yml` workflows, tdd-guard in `.claude/settings.json`.
3. Add `observability/` and `analytics/` before the first feature.
4. For Django, keep the rules; the composition root is the app config and
   the adapters are views and ORM repositories.
5. Delete what does not apply; keep the root under 150 lines and run the
   collection's `tools/check_templates.py` against your copy.
