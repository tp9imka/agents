# dart-flutter template

Copy `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` and
`agent_docs/` into the repository root, then:

1. Replace `<Project>`, the versions and the exemplar paths with real files.
2. Ship the gates the file names: `melos.yaml` scripts, root
   `analysis_options.yaml` with `import_lint` and the custom lints in
   `packages/core/lints`, `very_good_workflows` with `min_coverage: 100`,
   `mutation_test.yaml`, `lefthook.yml`. A rule without its gate is deleted
   from `AGENTS.md`.
3. Add `packages/core/observability` and `packages/core/analytics` before the first feature.
4. If you use Riverpod instead of bloc plus get_it, replace the DI and state
   sections in `agent_docs/architecture.md`; keep the constructor-injection rule.
5. Delete what does not apply; keep the root under 150 lines and run the
   collection's `tools/check_templates.py` against your copy.
