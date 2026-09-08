# Gates - Dart / Flutter

Rules in `CONSTITUTION.md` article VI.

## `melos run check`

`melos.yaml` `check` runs, in order, across all packages:

1. `dart format --set-exit-if-changed .`
2. `dart analyze --fatal-infos` (very_good_analysis plus the custom lints)
3. `import_lint` - layer and cross-feature rules
4. `melos run gen && git diff --exit-code -- '**/*.g.dart' '**/*.freezed.dart' '**/*.config.dart'` - codegen drift
5. `very_good test --coverage --min-coverage 100 --test-randomize-ordering-seed random` per package
6. `melos run test:goldens` - alchemist CI goldens

CI runs exactly `melos run check` through `very_good_workflows` (`flutter_package.yml` with `min_coverage: 100`).

## Fast subset

- `cd packages/features/orders/orders_ui && fvm flutter test` for one package
- `fvm flutter test test/order_cubit_test.dart --plain-name '<name>'` for one test
- `fvm dart format . && fvm dart analyze --fatal-infos` for one package

## CI

`.github/workflows/check.yml`: `subosito/flutter-action` with the version
from `.fvmrc`, `melos bootstrap`, `melos run check`. `update-goldens` job on
`main`. `nightly.yml`: `mutation_test` and the integration tests on an emulator.

## Hooks

`lefthook.yml`:

```yaml
pre-commit:
  commands:
    format:  { glob: "*.dart", run: "fvm dart format {staged_files} && git add {staged_files}" }
    analyze: { glob: "*.dart", run: "fvm dart analyze --fatal-infos {staged_files}" }
pre-push:
  commands:
    tests: { run: "melos run test" }
```

Agents: a Claude Code `Stop` hook runs `melos run check` and blocks until it
passes. No Dart TDD hook exists yet; review applies the stash check.

## Fail closed

A missing Flutter version, a missing golden or a codegen diff fails `check`.
