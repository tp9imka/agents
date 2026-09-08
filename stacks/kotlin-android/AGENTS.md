# AGENTS.md - <Project> (Kotlin / Android)

<Project> is an Android app: Kotlin <2.x>, Jetpack Compose (Material 3), single
activity, unidirectional data flow with `ViewModel` + `StateFlow`, Hilt, Room and
DataStore for local data, Retrofit/OkHttp for the network, WorkManager for
background work. Gradle modules: `app/`, `feature/<name>/{api,internal}`, `core/*`.
The seven articles of `CONSTITUTION.md` apply; each names its gate below.

## Commands

- Setup: JDK from `.java-version`, Android SDK path in `local.properties` (git-ignored). `./gradlew help` confirms the toolchain.
- Check (the CI gate): `./gradlew check` - ktlint, detekt, Konsist tests, unit tests, `koverVerify` (100% branch), Roborazzi verify, `apiCheck` drift.
- Build: `./gradlew assembleDebug`
- Test all: `./gradlew testDebugUnitTest`
- Test one class: `./gradlew :feature:orders:internal:testDebugUnitTest --tests "com.acme.orders.OrderViewModelTest"`
- Lint and format one module: `./gradlew :feature:orders:internal:ktlintFormat :feature:orders:internal:detekt`
- Screenshots: `./gradlew verifyRoborazziDebug`; goldens are recorded only in CI (`recordRoborazziDebug`).
- Coverage report: `./gradlew koverHtmlReport` => `build/reports/kover/html/index.html`
- Iterate with the single-module test task; run `./gradlew check` before declaring a task done.

## Architecture

- Feature-first modules: `:feature:<name>:api` (contracts, navigation entries, events) and `:feature:<name>:internal` (domain, use cases, ports, adapters, UI). Features depend on other features' `:api` only. Gate: Konsist test `core/testing/src/test/kotlin/ArchitectureTest.kt`.
- Dependency rule inside a feature: `domain` <= `application` <= `adapters`/`ui`. Nothing in `domain` imports `android.*`, Room, Retrofit or Compose. Gate: Konsist.
- DI: Hilt with constructor injection only; bindings live in `app/` and `feature/<name>/internal/src/main/kotlin/.../di/`. No `@Inject lateinit var`. Gate: Konsist rule `noFieldInjection`.
- UI: one `StateFlow<UiState>` per `ViewModel`, events as sealed classes, side effects only through use cases. Gate: Konsist (`*ViewModel` exposes no `MutableStateFlow`).
- Generated code (Hilt, Room, serialization) is never edited; regenerate. The public API surface of `:api` modules is tracked by `apiDump`; drift fails `check`.
- Layout and the rules in full: `agent_docs/architecture.md`.

## Testing

- Test-first: write the failing test, watch it fail, then implement. A change whose tests still pass with it stashed is not done. Gate: review runs `git stash && ./gradlew testDebugUnitTest` on the diff; no Kotlin TDD hook exists yet.
- Coverage: `koverVerify` fails below 100% branch coverage per module. Exclusions only via `@Generated` and the generated-package filter in `build-logic/src/main/kotlin/KoverConventionPlugin.kt`, each with a reason.
- Local tests: JUnit 5, kotest assertions, Turbine for flows. Fakes for own ports live in `core/testing`; MockK only for third-party SDK boundaries.
- Screen tests: `ComposeTestRule` with `ComponentActivity`; one Roborazzi screenshot per screen state.
- Mutation: `./gradlew pitest` on `core/*` and `feature/*/internal` runs nightly; a score under 80% fails the job.
- Time and randomness are injected (`Clock`, `Random`); `System.currentTimeMillis()` is forbidden in `main` sources. Gate: detekt `ForbiddenMethodCall`.
- Details and recipes: `agent_docs/testing.md`.

## Observability

- Every screen visit and every use-case call emits one canonical event through `core/observability` (`CanonicalEvent`: `event.name`, `trace_id`, `outcome`, `error.type`, `duration_ms`, `user.id`, business fields). `ObservedUseCase` and `ScreenObserver` emit it; feature code cannot skip it. Gate: `CanonicalEventTest` per feature.
- Logging goes through `core/observability/Logger` only. `android.util.Log`, `println` and direct `Timber` calls are forbidden. Gate: detekt `ForbiddenMethodCall`. Debug logs are stripped in release by `app/proguard-rules.pro`.
- Levels: `debug` (dev builds only), `info` (operators), `error` with `error.type`. A `warn` must be actionable, otherwise it is `info`.
- Privacy: never log tokens, message bodies or free text; ids are fine. Attributes are redacted in `core/observability/OtelExporterConfig.kt` before export.
- Usage events: the sealed class `core/analytics/AnalyticsEvent.kt` is the only catalogue; names are `object_action` in snake_case; no string event names at call sites. Gate: detekt rule `AnalyticsCatalogueOnly`.
- Performance: the OpenTelemetry Android agent reports cold and warm start, time to initial display, slow and frozen frames, ANRs and network spans. Sampling: 10% of `info` events, 100% of errors (`OtelExporterConfig.kt`).
- Setup, fields and the exporter: `agent_docs/observability.md`.

## Boundaries

- Always: run the module's test task after each change and `./gradlew check` before saying done; add a Konsist rule when you add an architectural rule; put new code in a `feature/*` or `core/*` module, never in `app/` except DI wiring and navigation.
- Ask first: adding a dependency to `gradle/libs.versions.toml`; changing module structure or a `:api` contract; bumping AGP, Kotlin or Compose versions; editing `build-logic/`.
- Never: commit secrets or `local.properties` (copy `secrets.properties.example`); edit generated code under `build/` (regenerate it); disable, delete or weaken a failing test (open a task and ask); call `android.util.Log` or `println` (use `Logger`); depend on another feature's `:internal` (use its `:api`); launch coroutines on `GlobalScope` (use `viewModelScope` or an injected `CoroutineScope`).

## Where to look

- `agent_docs/architecture.md` - module map, layer rules, DI wiring, the Konsist tests
- `agent_docs/testing.md` - test types, fakes, Roborazzi, Kover and PIT configuration
- `agent_docs/observability.md` - canonical event, logger, analytics catalogue, OTel agent, privacy
- `agent_docs/gates.md` - what `check` runs, the CI workflow, git hooks
- Exemplars: `feature/orders/internal/src/main/kotlin/com/acme/orders/ui/OrderViewModel.kt`, `feature/orders/internal/src/main/kotlin/com/acme/orders/data/OrdersRepositoryAdapter.kt`, `feature/orders/internal/src/test/kotlin/com/acme/orders/ui/OrderViewModelTest.kt`
- Legacy: none. When a legacy module appears, list it here and do not copy its patterns.

## Maintaining this file

- Add a line only after an observed failure, then re-run the task without and with the line and keep it only if the outcome changed. Every rule names its gate or its reason. Revisit after model releases. Stay under 150 lines (`tools/check_templates.py` in the collection enforces it).
