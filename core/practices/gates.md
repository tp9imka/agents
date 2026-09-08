# Gates

Constitution article VI. A gate nobody is forced to run is documentation.

## One command

Each project has one command that runs, in order: format check, lint, layer
gate, drift check for generated code, tests with coverage at threshold. It is
named in the first Commands block of `AGENTS.md`.

| Stack | Command |
|---|---|
| kotlin-android, java-spring | `./gradlew check` (with `koverVerify` / `jacocoTestCoverageVerification` and the Konsist / ArchUnit tests wired into `check`) |
| swift-ios | `make check` wrapping `swiftformat --lint`, `swiftlint --strict`, `xcodebuild test` and the coverage script |
| dart-flutter | `melos run check` or `make check` wrapping `dart format --set-exit-if-changed`, `dart analyze --fatal-infos`, `very_good test --coverage --min-coverage 100` |
| go | `make check` wrapping `gofmt`, `golangci-lint run`, `go-arch-lint check`, `go test -race -coverprofile`, `go-test-coverage` |
| rust | `just check` wrapping `cargo fmt --check`, `cargo clippy --all-targets -- -D warnings`, `cargo-modules` or workspace rules, `cargo llvm-cov nextest --fail-under-lines 100` |
| typescript-web | `pnpm check` wrapping biome or eslint, `tsc --noEmit`, `depcruise`, `vitest run --coverage` |
| python | `make check` wrapping `ruff format --check`, `ruff check`, `mypy`, `lint-imports`, `pytest --cov --cov-branch --cov-fail-under=100` |
| csharp-dotnet | `dotnet build -warnaserror` then `dotnet test` with coverlet thresholds and ArchUnitNET tests |

CI runs exactly that command. Nothing runs in CI that cannot run locally.

## Fast subset

`AGENTS.md` names the per-file forms (format one file, test one file, lint one
package) so an agent iterates in seconds and runs the full command before
declaring done.

## Layer gate

| Stack | Tool | What it checks |
|---|---|---|
| kotlin-android | Konsist test | feature modules do not depend on each other; only `:api` modules are imported; layer direction |
| java-spring | ArchUnit, Spring Modulith `verify()` | module boundaries, no cycles, layer direction |
| swift-ios | SPM targets per layer | the compiler enforces it; add a script that fails on cross-feature imports |
| dart-flutter | packages per layer (melos), `import_lint` | package boundaries; no `src/` imports across packages |
| go | go-arch-lint | component dependencies from `.go-arch-lint.yml` |
| rust | workspace crates, `cargo-modules` | crate graph; no adapter import in the domain crate |
| typescript-web | dependency-cruiser, Nx boundaries | forbidden paths, no cycles, feature isolation |
| python | import-linter | layers contract |
| csharp-dotnet | ArchUnitNET | project references and namespaces |

## Drift gate

Anything generated (API clients, DI graphs, mocks, tokens, docs from code) is
regenerated in the check command and `git diff --exit-code` fails on drift.

## Hooks for agents

- Pre-commit: the fast subset (format, lint, changed-package tests) via the
  stack's hooks manager (lefthook, pre-commit or prek, husky).
- Claude Code `PreToolUse`: tdd-guard / Probity where the stack has a reporter.
- Claude Code `Stop`: run the check command and block the turn until it passes;
  a second Stop hook may propose `AGENTS.md` updates from the transcript.
- Codex and Copilot: the check command in the PR workflow; the PR template
  requires the command output.

## Fail closed

A gate that cannot run fails the build; it does not skip. A missing tool is a
setup error, not a pass.

## Evidence

The house baseline's finding that enforcement was optional in five real
repos; Cloudflare and Airflow naming their enforcers; the verification ladder
in the Claude Code docs. [../evidence.md](../evidence.md), D5, D16.
