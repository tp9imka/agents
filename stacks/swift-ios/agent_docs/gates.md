# Gates - Swift / iOS

Rules in `CONSTITUTION.md` article VI.

## `make check`

`Makefile`, in order:

1. `swiftformat --lint .` (fix with `swiftformat .`)
2. `swiftlint --strict` (includes the custom rules in `.swiftlint.yml`)
3. `Scripts/check-layers.sh` - import direction per target
4. `swift test --package-path Packages/<each>` in parallel, then `xcodebuild test -scheme App` with coverage
5. `Scripts/coverage-gate.sh` - 100% regions per package
6. snapshot verification (part of the test run; goldens from CI)
7. `swift run tools api-dump --check` - public API drift on `<Feature>API` targets (optional, keep if you ship modules)

CI runs exactly `make check`.

## Fast subset

- `swift test --package-path Packages/Orders` for the package you changed
- `--filter OrderModelTests/<name>` for one test
- `swiftformat Packages/Orders && swiftlint --fix Packages/Orders`

## CI

`.github/workflows/check.yml`: macOS runner, `make bootstrap`, `make check`;
`record-snapshots` job on `main`; `nightly.yml` runs Muter and the UI tests on
a device farm.

## Hooks

`lefthook.yml`:

```yaml
pre-commit:
  commands:
    format: { glob: "*.swift", run: "swiftformat {staged_files} && git add {staged_files}" }
    lint:   { glob: "*.swift", run: "swiftlint --strict {staged_files}" }
pre-push:
  commands:
    tests: { run: "make test" }
```

Agents: a Claude Code `Stop` hook runs `make check` and blocks until it passes.
No Swift TDD hook exists yet; review applies the stash check.

## Fail closed

A missing Xcode version, a missing golden or a missing tool fails `make check`.
