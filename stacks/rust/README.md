# rust template

Copy `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` and
`agent_docs/` into the repository root, then:

1. Replace `<Project>`, `<1.8x>`, the framework names and the exemplar paths with real files.
2. Ship the gates the file names: `justfile` with `check`, workspace lints in
   `Cargo.toml`, `clippy.toml` `disallowed-methods`, `deny.toml`,
   `arch/allowed.txt` with `scripts/edges.sh`, `.cargo/llvm-cov.toml`,
   `lefthook.yml`, the `check.yml` / `nightly.yml` workflows, tdd-guard in
   `.claude/settings.json`.
3. Add `infra-observability` and `infra-analytics` before the first feature.
4. Delete what does not apply (Axum, sqlx); keep the root under 150 lines and
   run the collection's `tools/check_templates.py` against your copy.
