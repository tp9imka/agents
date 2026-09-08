# Architecture - Kotlin / Android

Read when adding a module, a feature, a port or a binding.

## Module map

```
app/                                  composition root: Hilt @HiltAndroidApp, NavHost, DI bindings of :internal to :api
feature/<name>/api/                   contracts other features may use: navigation entry, public events, small models
feature/<name>/internal/              the slice
  src/main/kotlin/.../domain/         entities, value classes, domain services - pure Kotlin, no android.* imports
  src/main/kotlin/.../application/    use cases (one class per use case), ports (interfaces owned here)
  src/main/kotlin/.../data/           driven adapters: Room DAOs, Retrofit services, repository implementations
  src/main/kotlin/.../ui/             Compose screens, ViewModel, UiState, UiEvent
  src/main/kotlin/.../di/             Hilt module binding ports to adapters
  src/test/kotlin/...                 tests mirror the main tree
core/observability/                   CanonicalEvent, Logger, OTel setup, redaction
core/analytics/                       AnalyticsEvent catalogue and the tracker port
core/network/, core/database/         shared infrastructure, no feature knowledge
core/design/                          design system: theme, tokens, components
core/testing/                         fakes for core ports, test rules, the Konsist architecture tests
build-logic/                          convention plugins: android library, compose, kover, detekt, ktlint
gradle/libs.versions.toml             the only place versions live
```

## Layer rules

- `domain` imports nothing from `android.*`, `androidx.*`, Room, Retrofit, Compose or `core/network`.
- `application` depends on `domain` and defines ports as interfaces; it may not import `data` or `ui`.
- `data` implements ports; it may import `domain` and `application` types, never `ui`.
- `ui` depends on `application` (use cases) and `domain` (values), never on `data`.
- A feature's `internal` module depends on other features only through their `api`.
- `app` is the only module that depends on `internal` modules, for wiring.

## The Konsist gate

`core/testing/src/test/kotlin/ArchitectureTest.kt` runs in `./gradlew check`:

```kotlin
class ArchitectureTest {
    private val scope = Konsist.scopeFromProject()

    @Test fun `layers point inward`() = scope.assertArchitecture {
        val domain = Layer("domain", "com.acme..domain..")
        val application = Layer("application", "com.acme..application..")
        val data = Layer("data", "com.acme..data..")
        val ui = Layer("ui", "com.acme..ui..")
        domain.dependsOnNothing()
        application.dependsOn(domain)
        data.dependsOn(domain, application)
        ui.dependsOn(domain, application)
    }

    @Test fun `domain has no android imports`() =
        scope.files.withPackage("com.acme..domain..").imports
            .assertFalse { it.name.startsWith("android") || it.name.startsWith("androidx") }

    @Test fun `no field injection`() =
        scope.properties().withAnnotationOf(Inject::class).assertFalse { it.hasLateinitModifier }

    @Test fun `view models expose read-only state`() =
        scope.classes().withNameEndingWith("ViewModel").properties()
            .withPublicOrDefaultModifier().assertFalse { it.type?.name?.startsWith("MutableStateFlow") == true }

    @Test fun `features depend on api modules only`() =
        scope.files.withPathContaining("/feature/").withPathContaining("/internal/")
            .imports.assertFalse { it.name.matches(Regex("com\\.acme\\.(?!${OWN_FEATURE})\\w+\\.internal\\..*")) }
}
```

Adjust the package prefix. Every new architectural rule gets a test here in the
same change.

## Dependency injection

- Constructor injection with `@Inject constructor(...)`; `@Binds` in the feature's `di/` module for port to adapter; scopes are explicit (`@ViewModelScoped`, `@Singleton`).
- `app/` holds `@HiltAndroidApp`, navigation wiring and nothing else.
- A composition-root smoke test: `app/src/test/kotlin/DiGraphTest.kt` builds the graph with `HiltAndroidTest` on Robolectric so a missing binding fails `check`, not the first launch.
- KMP variant: replace Hilt with Koin plus the Koin compiler plugin (`koin-annotations`, verify at compile time); the rules above do not change.

## Navigation and state

- Navigation entries are declared in `:api` (`OrdersEntry.route`) and composed in `app/`; features never import each other's screens.
- `UiState` is an immutable data class; `UiEvent` a sealed interface; the `ViewModel` reduces events into state and calls use cases for effects.
- Persisted state uses `SavedStateHandle`; process death is a test case.

## Size and placement

- A `ViewModel` above 300 lines or a use case above 150 lines is a signal to split by responsibility.
- New shared code goes to `core/*` only when a second feature needs it.
