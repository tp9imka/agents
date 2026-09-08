# AGENTS.md - <Project> (Java or Kotlin / Spring Boot)

<Project> is a Spring Boot <3.x> service on Java <21> (or Kotlin <2.x>),
Gradle with the wrapper, Spring Modulith modules per bounded context, JPA
with Postgres and Flyway, Micrometer tracing with OpenTelemetry. Layout:
`src/main/java/com/acme/<module>/{domain,application,adapters}`,
`src/main/java/com/acme/Application.java` as the composition root, tests
mirroring `src/main`. The seven articles of `CONSTITUTION.md` apply; each
names its gate below.

## Commands

- Setup: JDK from `.sdkmanrc` (`sdk env`); `./gradlew --version` confirms it. Always the wrapper, never a global Gradle.
- Check (the CI gate): `./gradlew check` - Spotless, Checkstyle or detekt, ArchUnit tests, Spring Modulith `verify`, Flyway drift check, unit and integration tests, `jacocoTestCoverageVerification` (100% branch), API drift.
- Build: `./gradlew build`; run: `./gradlew bootRun --args='--spring.profiles.active=local'`
- Test all: `./gradlew test`
- Test one class or method: `./gradlew test --tests "com.acme.orders.application.PlaceOrderTest.returnsErrorWhenCartIsEmpty"`
- Integration tests (Testcontainers Postgres, needs Docker): `./gradlew integrationTest`
- Format and lint: `./gradlew spotlessApply checkstyleMain` (Kotlin: `spotlessApply detekt`)
- Coverage report: `./gradlew jacocoTestReport` => `build/reports/jacoco/test/html/index.html`
- Migrations: add `src/main/resources/db/migration/V<n>__<what>.sql`; never edit an applied one.
- Iterate with `--tests`; run `./gradlew check` before declaring done.

## Architecture

- Modules per bounded context as Spring Modulith application modules (`com.acme.<module>`); other modules use a module's published API package (`com.acme.<module>.api`) or its application events only; internals are package-private. Gate: `ApplicationModules.of(Application.class).verify()` in `ModularityTest` and ArchUnit rules in `ArchitectureTest`, both in `check`.
- Dependency rule inside a module: `domain` <= `application` <= `adapters` (`web`, `persistence`, `messaging`). `domain` has no Spring, JPA or Jackson annotations. Gate: ArchUnit `layeredArchitecture()`.
- DI: constructor injection only (final fields, no `@Autowired` on fields); beans are stateless; wiring is component scanning within modules plus explicit `@Configuration` in `adapters`. Gate: ArchUnit rule `noFieldInjection`.
- Web contract: controllers map DTOs (records with Bean Validation) to commands, call one use case, map results and errors with `@ControllerAdvice`; JPA entities never leave `adapters`. Gate: ArchUnit rule `entitiesStayInAdapters`.
- Generated code (MapStruct, OpenAPI clients, jOOQ) is never edited; drift fails `check`.
- Layout and rules in full: `agent_docs/architecture.md`.

## Testing

- Test-first: the failing test comes first; a change whose tests pass with it stashed is not done. Gate: review runs `git stash && ./gradlew test` on the diff; no JVM TDD hook exists yet.
- Coverage: `jacocoTestCoverageVerification` fails below 100% BRANCH and LINE per class; excludes only generated classes and `Application.java`, listed in `build.gradle.kts` with a reason. Exclusions in code only: `@Generated` on generated code, never on hand-written classes.
- Tests: JUnit 5 with `@Nested` and `@DisplayName` behaviours (Kotlin: kotest BehaviorSpec), AssertJ, fakes for own ports in `src/testFixtures`, `@WebMvcTest` slices for controllers, `@DataJpaTest` with Testcontainers for repositories, `@ApplicationModuleTest` for module integration, Mockito only for third-party clients.
- Mutation: `./gradlew pitest` on `domain` and `application` packages nightly; a score under 80% fails.
- Time and randomness are injected (`Clock` bean, `RandomGenerator`); `LocalDateTime.now()` and `Instant.now()` without a `Clock` are forbidden. Gate: ArchUnit rule `noSystemClock`.
- Recipes: `agent_docs/testing.md`.

## Observability

- Every request, job and message emits one canonical event through `com.acme.observability` (`CanonicalEvent`: `event.name`, `trace_id`, `outcome`, `error.type`, `duration_ms`, `user.id`, business fields) from `CanonicalEventFilter` (servlet filter) and `ObservedListener` for messaging, in `finally`; use cases add fields with `Observe.add(...)`. Gate: `CanonicalEventTest` asserts the event on 200 and on an exception.
- Logging: SLF4J via `LoggerFactory` with Spring Boot structured logging (`logging.structured.format.console=ecs`); MDC carries `trace_id` and `span_id` from Micrometer. `System.out`, `System.err` and `printStackTrace` are forbidden. Gate: ArchUnit `noSystemOut` plus Checkstyle `Regexp`.
- Levels: `DEBUG` (dev), `INFO`, `ERROR` with `error.type`; a `WARN` must be actionable. Libraries throw; the boundary logs once.
- Privacy: never log tokens, message bodies or free text; ids are fine. The logback `MaskingPatternLayout` in `logback-spring.xml` masks `password|token|secret|body|content|authorization`.
- Usage events: `com.acme.analytics.AnalyticsEvent` (a sealed interface with records) is the catalogue; names `object_action` snake_case; `Tracker.track(AnalyticsEvent)` only. Gate: the sealed hierarchy plus ArchUnit forbidding the vendor SDK outside `analytics`.
- Performance: Micrometer Observation API with OpenTelemetry tracing and OTLP export; the four golden signals per endpoint from `http.server.requests`; JDBC and messaging spans; JFR for profiling. Sampling: `management.tracing.sampling.probability=0.1`, errors always (custom sampler); retention default 30 days.
- Setup and fields: `agent_docs/observability.md`.

## Boundaries

- Always: run the class's tests after each change and `./gradlew check` before saying done; add an ArchUnit rule when you add an architectural rule; put new code in a `com.acme.<module>` package, never in the root package except `Application.java`.
- Ask first: adding a dependency to `gradle/libs.versions.toml`; changing a module's `api` package or events; adding a module; altering an existing table in place; bumping Java, Kotlin or Spring Boot; editing `build-logic/`, `checkstyle.xml` or `.github/workflows/`.
- Never: commit secrets or `application-local.yml` (use `application-local.yml.example` and environment variables); edit an applied migration (add a new `V<n>__` file); disable or delete a failing test or add `@Disabled` to get green (ask); use `System.out` or `printStackTrace` (use the SLF4J logger); use field injection (constructor); expose a JPA entity from a controller (map to a DTO); call another module's internals (use its `api` package or an event).

## Where to look

- `agent_docs/architecture.md` - module map, ArchUnit and Modulith rules, wiring, web contract
- `agent_docs/testing.md` - test slices, fixtures, Testcontainers, JaCoCo config, PIT
- `agent_docs/observability.md` - canonical event filter, structured logging, catalogue, Micrometer and OTel, privacy
- `agent_docs/gates.md` - what `check` runs, CI, hooks
- Exemplars: `src/main/java/com/acme/orders/application/PlaceOrder.java`, `src/main/java/com/acme/orders/adapters/persistence/JpaOrdersRepository.java`, `src/test/java/com/acme/orders/application/PlaceOrderTest.java`
- Legacy: none. When a legacy module appears, list it here and do not copy its patterns.

## Maintaining this file

- Add a line only after an observed failure, then re-run the task without and with the line and keep it only if the outcome changed. Every rule names its gate or its reason. Revisit after model releases. Stay under 150 lines.
