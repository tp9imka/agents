# go template

Copy `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` and
`agent_docs/` into the repository root, then:

1. Replace `<Project>`, `<1.2x>`, the transports and the exemplar paths with real files.
2. Ship the gates the file names: `Makefile` with `check`, `.golangci.yml`
   with `forbidigo`, `depguard`, `errorlint`, `wrapcheck`, `gochecknoglobals`,
   `gochecknoinits`; `.go-arch-lint.yml`; `.testcoverage.yml`; `lefthook.yml`;
   the `check.yml` / `nightly.yml` workflows; tdd-guard in `.claude/settings.json`.
3. Add `pkg/observability` and `pkg/analytics` before the first feature.
4. Delete what does not apply (gRPC, worker); keep the root under 150 lines
   and run the collection's `tools/check_templates.py` against your copy.
