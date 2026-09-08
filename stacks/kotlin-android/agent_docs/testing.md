# Testing - Kotlin / Android

Read before writing or changing tests. The rules are in `CONSTITUTION.md`
articles II and III; this page is how they run here.

## Workflow

1. Name the modules and types the change touches. Two sentences in the task.
2. List the tests as a checklist with behaviour names:
   `returns_error_when_order_is_empty`, `emits_loading_then_orders`.
3. Per test: write it, run `./gradlew :feature:orders:internal:testDebugUnitTest --tests "..."`,
   confirm it fails for the right reason, implement the minimum, run the module's
   tests, refactor green.
4. Structural commits (rename, move, extract) are separate from behavioural ones.
5. Before done: `./gradlew check`. Coverage must read 100% for the module.

## Test types and where they live

| Level | Tool | Location | Runs in |
|---|---|---|---|
| unit (domain, use cases, ViewModel) | JUnit 5, kotest assertions, Turbine | `feature/<x>/internal/src/test` | `testDebugUnitTest` |
| adapter (Room, Retrofit) | Robolectric + in-memory Room; MockWebServer | `feature/<x>/internal/src/test` | `testDebugUnitTest` |
| screen | `ComposeTestRule` with `ComponentActivity`, Robolectric | `feature/<x>/internal/src/test` | `testDebugUnitTest` |
| screenshot | Roborazzi | same, `verifyRoborazziDebug` | `check` |
| instrumented | Gradle-managed devices | `app/src/androidTest` | nightly |

Fakes for own ports live in `core/testing` (`FakeOrdersPort`, `FakeClock`,
`FakeTracker`). MockK is allowed only at third-party SDK boundaries.

## Coverage gate

`build-logic/src/main/kotlin/KoverConventionPlugin.kt` applies to every module:

```kotlin
kover {
    reports {
        filters {
            excludes {
                annotatedBy("javax.annotation.processing.Generated", "dagger.internal.DaggerGenerated")
                packages("*.databinding", "*.di")        // generated + composition root
                classes("*_Factory", "*_HiltModules*", "*ComposableSingletons*")
            }
        }
        verify {
            rule("branches") { minBound(100, CoverageUnit.BRANCH) }
            rule("lines") { minBound(100, CoverageUnit.LINE) }
        }
    }
}
```

`check` depends on `koverVerify`. Any other exclusion is an `@Generated`
annotation with a reason in the same line. Never lower `minBound`.

## Mutation

PIT via `gradle-pitest-plugin` on `core/*` and `feature/*/internal`:
`./gradlew pitest`, threshold `mutationThreshold = 80`, scheduled nightly in
`.github/workflows/nightly.yml`. A falling score with stable coverage means
assertion-free tests were added.

## Screenshots

Roborazzi records goldens in CI (`recordRoborazziDebug` on `main`), verifies on
every PR. Never commit goldens from a workstation; the renderer differs.

## Rules

- Time, randomness and dispatchers are injected: `Clock`, `Random`, `CoroutineDispatchers`.
- Test the failure path first: every `Result.failure` and every `catch` has a test.
- No tests for constants, no negative tests for removed code, no assertion-free tests.
- Test names are behaviours in backticks or snake_case; one behaviour per test.
- Flaky tests are quarantined with `@Tag("flaky")` and a linked task, not deleted.
