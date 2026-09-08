# Gates - Java or Kotlin / Spring Boot

Rules in `CONSTITUTION.md` article VI.

## `./gradlew check`

`build.gradle.kts` wires `check` to depend on, in order:

1. `spotlessCheck` (`spotlessApply` fixes) - google-java-format or ktfmt
2. `checkstyleMain` (Kotlin: `detekt`) - includes the `System.out` regexp check
3. `test` - unit and slice tests, `ArchitectureTest`, `ModularityTest`, `ApplicationContextTest`
4. `integrationTest` - Testcontainers Postgres, `@ApplicationModuleTest`, Flyway from empty and from the previous schema
5. `jacocoTestCoverageVerification` - 100% branch and line per class (Kover in Kotlin)
6. `openApiCheck` - generated OpenAPI snapshot diff; `flywayValidate` for migration drift

CI runs exactly `./gradlew check --no-daemon` with Docker available.

## Fast subset

- `./gradlew test --tests "com.acme.orders.application.PlaceOrderTest"` for one class
- `--tests "...PlaceOrderTest.returnsErrorWhenCartIsEmpty"` for one method
- `./gradlew spotlessApply checkstyleMain` for formatting and lint
- Gradle configuration cache and build cache on in `gradle.properties`; `--continuous` while iterating

## CI

`.github/workflows/check.yml`: `actions/setup-java` with the version from
`.sdkmanrc`, `gradle/actions/setup-gradle`, `./gradlew check`.
`nightly.yml`: `./gradlew pitest`.

## Hooks

`lefthook.yml`:

```yaml
pre-commit:
  commands:
    format: { glob: "*.{java,kt}", run: "./gradlew spotlessApply -q && git add {staged_files}" }
pre-push:
  commands:
    test: { run: "./gradlew test -q" }
```

Agents: a Claude Code `Stop` hook runs `./gradlew check` and blocks until it
passes (`.claude/settings.json`). No JVM TDD hook exists yet; review applies
the stash check from `agent_docs/testing.md`.

## Fail closed

A missing Docker daemon, a migration drift or a coverage miss fails `check`; nothing skips.
