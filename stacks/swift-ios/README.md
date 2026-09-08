# swift-ios template

Copy `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` and
`agent_docs/` into the repository root, then:

1. Replace `<Project>`, `<6.x>`, `<17>` and the exemplar paths with real files.
2. Ship the gates the file names: `Scripts/check-layers.sh`,
   `Scripts/coverage-gate.sh` + `coverage_check.py`, `.swiftlint.yml` with the
   custom rules, `.swiftformat`, `muter.conf.yml`, `lefthook.yml`, the
   `check.yml` / `nightly.yml` workflows. A rule without its gate is deleted
   from `AGENTS.md`.
3. Add `Packages/Observability` and `Packages/Analytics` before the first feature.
4. Choose `@Observable` models or TCA and delete the other from
   `agent_docs/architecture.md`.
5. Delete what does not apply; keep the root under 150 lines and run the
   collection's `tools/check_templates.py` against your copy.
