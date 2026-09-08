# csharp-dotnet template

Copy `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` and
`agent_docs/` into the repository root, then:

1. Replace `<Project>`, `<9>`, `Acme` and the exemplar paths with real files.
2. Ship the gates the file names: `check.sh`, `Directory.Build.props` with
   warnings as errors and the banned-API analyzer, `BannedSymbols.txt`,
   `Directory.Build.targets` with the coverlet thresholds,
   `tests/Architecture.Tests`, `stryker-config.json`, `lefthook.yml`, the
   `check.yml` / `nightly.yml` workflows.
3. Add `src/Shared/Observability` and `src/Shared/Analytics` before the first module.
4. For MAUI, keep the rules; the composition root is `MauiProgram.cs`, the
   unidirectional-flow section of the core applies to ViewModels, and
   screenshot tests replace endpoint tests.
5. Delete what does not apply; keep the root under 150 lines and run the
   collection's `tools/check_templates.py` against your copy.
