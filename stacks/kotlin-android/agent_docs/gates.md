# Gates - Kotlin / Android

What runs, where, and how to make it fast. Rules in `CONSTITUTION.md` article VI.

## `./gradlew check`

Wired in `build-logic/src/main/kotlin/QualityConventionPlugin.kt` so every
module's `check` depends on, in order:

1. `ktlintCheck` - formatting; `ktlintFormat` fixes.
2. `detekt` - lint including `ForbiddenMethodCall` and the custom analytics rule.
3. `testDebugUnitTest` - unit, adapter and screen tests, including the Konsist `ArchitectureTest`.
4. `koverVerify` - 100% branch and line per module.
5. `verifyRoborazziDebug` - screenshot diff against CI-recorded goldens.
6. `apiCheck` - binary-compatibility validator on `:api` modules; drift fails.

Nothing runs in CI that this command does not run.

## Fast subset

- One module's tests: `./gradlew :feature:orders:internal:testDebugUnitTest`
- One class: add `--tests "com.acme.orders.OrderViewModelTest"`
- Lint one module: `./gradlew :feature:orders:internal:detekt`
- Gradle configuration cache and build cache are on in `gradle.properties`.

## CI

`.github/workflows/check.yml`: on pull request and push to `main`, one job
running `./gradlew check --no-daemon` with the Gradle cache action;
`record-goldens` job on `main` runs `recordRoborazziDebug` and commits goldens;
`nightly.yml` runs `pitest` and the Gradle-managed-device tests.

## Hooks

`lefthook.yml`:

```yaml
pre-commit:
  parallel: true
  commands:
    ktlint:
      glob: "*.kt"
      run: ./gradlew ktlintFormat -q && git add {staged_files}
    detekt:
      glob: "*.kt"
      run: ./gradlew detekt -q
pre-push:
  commands:
    tests:
      run: ./gradlew testDebugUnitTest -q
```

Agents: a Claude Code `Stop` hook runs `./gradlew check` and blocks the turn
until it passes (`.claude/settings.json`). No TDD hook exists for Kotlin yet;
review applies the stash check from `agent_docs/testing.md`.

## Fail closed

A missing SDK, a missing golden or a missing tool fails `check`; nothing skips.
