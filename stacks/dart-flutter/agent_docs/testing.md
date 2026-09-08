# Testing - Dart / Flutter

Rules in `CONSTITUTION.md` articles II and III.

## Workflow

1. Name the packages and types the change touches, in the task.
2. List the tests with behaviour names: `emits loaded when orders are fetched`, `emits failure when network fails`.
3. Per test: write it, run `fvm flutter test test/order_cubit_test.dart --plain-name '<name>'`, see it fail for the right reason, implement the minimum, run the package tests, refactor green.
4. Structural commits separate from behavioural ones.
5. Before done: `melos run check`; every package touched reads 100%.

## Test types

| Level | Tool | Location |
|---|---|---|
| unit (domain, use cases) | `test` | `<name>_domain/test` |
| cubit | `bloc_test` (`blocTest(build:, act:, expect:)`) | `<name>_ui/test` |
| adapter | `test` with `http_mock_adapter` for dio, in-memory drift | `<name>_data/test` |
| widget | `flutter_test` with `pumpApp` from `test_support` | `<name>_ui/test` |
| golden | alchemist `goldenTest` per state | `<name>_ui/test/goldens` |
| integration | `integration_test`, few, nightly | `apps/<app>/integration_test` |

Fakes for own ports live in `packages/core/test_support`; `mocktail` only for
third-party boundaries (`registerFallbackValue` for custom types).

## Coverage gate

`melos.yaml`:

```yaml
scripts:
  test:
    exec: very_good test --coverage --min-coverage 100 --test-randomize-ordering-seed random --exclude-coverage "**/*.g.dart,**/*.freezed.dart,**/*.config.dart,**/injection.dart"
    packageFilters: { dirExists: test }
```

Line coverage (Dart has no branch coverage). Exclusions in code only:

```dart
// coverage:ignore-start  reason: platform channel, exercised by integration test
...
// coverage:ignore-end
```

Never lower `--min-coverage`; never add a pattern to `--exclude-coverage`
for hand-written code.

## Mutation

`mutation_test` on `packages/features/*_domain` in `nightly.yml` with a
minimum score of 80 in `mutation_test.yaml`.

## Goldens

alchemist with `platformGoldens` off in CI and `ciGoldens` on; goldens are
updated only by the `update-goldens` job on `main`. A golden diff on a PR
means a visual change to review, not a file to regenerate locally.

## Rules

- `Clock` and `Random` are injected; `DateTime.now()` in `lib/` fails the custom lint.
- Failure path first: every `Failure` state and every thrown exception has a test.
- No tests for constants, no assertion-free tests, no `skip:` without a linked task.
- One behaviour per test; names are sentences.
- Widget tests assert behaviour (a tap adds an event) and goldens assert appearance; do not duplicate.
