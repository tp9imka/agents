# Architecture - Java or Kotlin / Spring Boot

A modular monolith: Spring Modulith modules per bounded context, hexagonal
layers inside each, both verified by tests that run in `check`.

## Package map

```
com.acme.Application                       composition root: @SpringBootApplication, nothing else
com.acme.<module>/
  api/                                     what other modules may call: interfaces, records, events (public)
  domain/                                  entities as plain classes or records, value objects, invariants, domain errors; no Spring, JPA, Jackson
  application/                             use cases (one class per use case), ports (interfaces), commands and results (records)
  adapters/web/                            controllers, request/response records with Bean Validation, ControllerAdvice
  adapters/persistence/                    JPA entities, Spring Data repositories, port implementations, mappers
  adapters/messaging/                      listeners and publishers
  package-info.java                        @ApplicationModule(allowedDependencies = {"users::api"})
com.acme.observability/                    CanonicalEvent, CanonicalEventFilter, Observe, masking, tracing config
com.acme.analytics/                        AnalyticsEvent sealed interface, Tracker
com.acme.shared/                           value types used by every module; depends on nothing
src/testFixtures/java/                     fakes for shared ports, test data builders
```

Everything outside `api/` is package-private or module-internal; Spring
Modulith treats the module's root package as the API by default, so put the
public surface in `api/` and mark the rest with `@ApplicationModule(type = OPEN)` never.

## The gates

`src/test/java/com/acme/ModularityTest.java`:

```java
class ModularityTest {
    ApplicationModules modules = ApplicationModules.of(Application.class);
    @Test void modulesAreValid() { modules.verify(); }
    @Test void writeDocs() { new Documenter(modules).writeDocumentation(); }
}
```

`src/test/java/com/acme/ArchitectureTest.java` (ArchUnit):

```java
@AnalyzeClasses(packages = "com.acme", importOptions = DoNotIncludeTests.class)
class ArchitectureTest {
    @ArchTest static final ArchRule layers = layeredArchitecture().consideringOnlyDependenciesInLayers()
        .layer("domain").definedBy("..domain..")
        .layer("application").definedBy("..application..")
        .layer("adapters").definedBy("..adapters..")
        .whereLayer("domain").mayNotAccessAnyLayer()
        .whereLayer("application").mayOnlyAccessLayers("domain")
        .whereLayer("adapters").mayOnlyAccessLayers("domain", "application");
    @ArchTest static final ArchRule domainIsPure = noClasses().that().resideInAPackage("..domain..")
        .should().dependOnClassesThat().resideInAnyPackage("org.springframework..", "jakarta.persistence..", "com.fasterxml..");
    @ArchTest static final ArchRule noFieldInjection = noFields().should().beAnnotatedWith(Autowired.class);
    @ArchTest static final ArchRule entitiesStayInAdapters = classes().that().areAnnotatedWith(Entity.class)
        .should().resideInAPackage("..adapters.persistence..");
    @ArchTest static final ArchRule noSystemOut = noClasses().should().callMethod(PrintStream.class, "println", String.class)
        .orShould().accessField(System.class, "out").orShould().accessField(System.class, "err");
    @ArchTest static final ArchRule noSystemClock = noClasses().that().resideOutsideOfPackage("..observability..")
        .should().callMethod(Instant.class, "now").orShould().callMethod(LocalDateTime.class, "now");
    @ArchTest static final ArchRule noCycles = slices().matching("com.acme.(*)..").should().beFreeOfCycles();
}
```

Add a rule here in the same change as any new architectural rule.

## Wiring

- Constructor injection; `final` fields; no `@Autowired` on fields or setters.
- Ports are interfaces in `application`; adapters implement them and are found by component scanning inside the module; cross-module calls go through `api` interfaces or `ApplicationEventPublisher` events (Modulith event publication registry for reliability).
- `@Configuration` classes live in `adapters` and configure only that adapter's technology.
- A context-load smoke test (`ApplicationContextTest`) fails `check` on a missing bean.

## Web contract

1. Controller method receives a `record` with Bean Validation annotations.
2. Maps it to a command record and calls exactly one use case.
3. Maps the result to a response record; domain errors are translated in `ControllerAdvice` to RFC 9457 problem details.
4. JPA entities never appear in a controller or a response.

## Kotlin variant

Same packages; data classes for records, `internal` for module internals in
addition to the Modulith check, detekt instead of Checkstyle, kotest
BehaviorSpec for behaviours, Kover instead of JaCoCo (`minBound(100)`).

## Size

- A use case above 150 lines or a controller above 200 lines is split.
- Shared code moves to `com.acme.shared` only when a second module needs it.
