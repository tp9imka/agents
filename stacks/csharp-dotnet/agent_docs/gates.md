# Gates - C# / .NET

Rules in `CONSTITUTION.md` article VI.

## The check target

`check.sh` (or a Cake `Check` target), in order:

```bash
dotnet format --verify-no-changes
dotnet build -warnaserror
dotnet test tests/Architecture.Tests
dotnet ef migrations has-pending-model-changes --project src/Modules/Orders/Orders.Infrastructure   # per module; fails on drift
dotnet test                                     # coverlet thresholds from Directory.Build.targets
dotnet run --project tools/ApiCheck              # PublicAPI.*.txt drift (or Microsoft.CodeAnalysis.PublicApiAnalyzers in the build)
```

CI runs exactly this script with Docker available for `tests/Integration.Tests`.

## Fast subset

- `dotnet test tests/Orders.Tests --filter "FullyQualifiedName~PlaceOrderTests"` for one class
- `--filter "FullyQualifiedName~PlaceOrderTests.ReturnsErrorWhenCartIsEmpty"` for one method
- `dotnet format src/Modules/Orders` and `dotnet build src/Modules/Orders/Orders.Application`
- `dotnet watch test --project tests/Orders.Tests` while iterating

## CI

`.github/workflows/check.yml`: `actions/setup-dotnet` with `global.json`,
`dotnet tool restore`, `./check.sh`. `nightly.yml`: `dotnet stryker`.

## Hooks

`lefthook.yml`:

```yaml
pre-commit:
  commands:
    format: { glob: "*.cs", run: "dotnet format --include {staged_files} && git add {staged_files}" }
pre-push:
  commands:
    build: { run: "dotnet build -warnaserror" }
    test:  { run: "dotnet test --no-build" }
```

Agents: a Claude Code `Stop` hook runs `./check.sh` and blocks until it
passes (`.claude/settings.json`). No .NET TDD hook exists yet; review applies
the stash check from `agent_docs/testing.md`.

## Fail closed

A missing SDK version, a migration drift or a threshold miss fails the check target; nothing skips.
