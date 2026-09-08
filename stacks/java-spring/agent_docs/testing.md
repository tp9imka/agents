# Testing - Java or Kotlin / Spring Boot

Rules in `CONSTITUTION.md` articles II and III.

## Workflow

1. Name the module and types the change touches, in the task.
2. List the tests with behaviour names: `returnsErrorWhenCartIsEmpty`, `persistsOrderAndPublishesEvent`.
3. Per test: write it, run `./gradlew test --tests "com.acme.orders.application.PlaceOrderTest.<name>"`, see it fail for the right reason, implement the minimum, run the class, refactor green.
4. Structural commits separate from behavioural ones.
5. Before done: `./gradlew check`; every class touched reads 100% branch and line.

## Test types

| Level | Tool | Location | Task |
|---|---|---|---|
| unit (domain, use cases) | JUnit 5 `@Nested` + `@DisplayName`, AssertJ; kotest BehaviorSpec in Kotlin | `src/test` | `test` |
| web slice | `@WebMvcTest` + `MockMvc` with the use case faked | `src/test` | `test` |
| persistence | `@DataJpaTest` + Testcontainers Postgres | `src/integrationTest` | `integrationTest` |
| module | `@ApplicationModuleTest` with `Scenario` for events | `src/integrationTest` | `integrationTest` |
| contract | OpenAPI snapshot via `springdoc` diff | `src/test` | `test` |

Fakes for own ports live in `src/testFixtures` (`InMemoryOrdersRepository`,
`FixedClock`, `RecordingTracker`). Mockito only for third-party clients.

## Coverage gate

`build.gradle.kts`:

```kotlin
tasks.jacocoTestCoverageVerification {
    violationRules {
        rule {
            element = "CLASS"
            excludes = listOf("com.acme.Application", "*MapperImpl", "*Config", "*.generated.*") // composition root, generated
            limit { counter = "BRANCH"; minimum = "1.00".toBigDecimal() }
            limit { counter = "LINE";   minimum = "1.00".toBigDecimal() }
        }
    }
}
tasks.check { dependsOn(tasks.jacocoTestCoverageVerification) }
```

Exclusions in code only via `@Generated` on generated classes. Never lower
`minimum`; never add a hand-written class to `excludes`. Kotlin: Kover with
`minBound(100, CoverageUnit.BRANCH)`.

## Mutation

`gradle-pitest-plugin` with `targetClasses = ["com.acme.*.domain.*", "com.acme.*.application.*"]`,
`mutationThreshold = 80`; `./gradlew pitest` in `nightly.yml`.

## Rules

- `Clock` is a bean (`Clock.systemUTC()` in `observability`, `Clock.fixed(...)` in tests); `Instant.now()` without it fails ArchUnit.
- Failure path first: every thrown domain exception and every error response has a test.
- No tests for constants, no assertion-free tests, no `@Disabled` without a linked task.
- Structured log assertions with `OutputCaptureExtension` parsed as JSON, never substring matches on prose.
- Flyway migrations are tested by the Testcontainers run against an empty database and against the previous release's schema.
