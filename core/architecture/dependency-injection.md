# Dependency injection

Constitution article V. Injection makes the dependency rule and the 100% rule
reachable: a class that builds its own collaborators cannot be tested at the
port.

## Rules

- Required dependencies come through the constructor. No field injection, no
  setter injection, no service-locator lookups inside a class.
- Wiring happens once, at the composition root. A locator, if the stack has
  one, is called only there and in test setup.
- Prefer a compile-time or generated graph: a missing binding is a build
  failure, not a runtime crash.
- Interfaces (ports) are injected; concrete adapters are bound at the root.
  Name adapters by technology, never with an `Impl` suffix: `JpaOrderRepository`,
  `InMemoryOrderRepository`.
- Tests inject fakes through the same constructors. Unstubbed dependencies
  should fail loudly in tests.
- A composition-root smoke test builds the full graph in CI.

## Per stack

| Stack | Default | Alternative | Notes |
|---|---|---|---|
| kotlin-android | Hilt | Koin with the compiler plugin (KMP), Metro | bindings only in the app or `app-common` module |
| java-spring | Spring constructor injection | Guice | no field `@Autowired`; beans stateless |
| swift-ios | swift-dependencies | Factory, plain initialisers with a `@Environment` for SwiftUI-owned state | `testValue` unimplemented by default so tests fail on unstubbed access |
| dart-flutter | get_it + injectable (generated graph) | Riverpod (state and DI together) | `configureDependencies()` is the root; never `getIt<T>()` inside features |
| go | constructors wired in `main` / `internal/app` | Fx for large services | no package-level globals, no `init()` wiring; Wire is archived |
| rust | generics and trait objects wired in `main` | none | `Arc<dyn Port>` at the boundary; no global state |
| typescript-web | constructor injection; NestJS providers on the server | inversify, tsyringe | interfaces need a `Symbol` token in NestJS |
| python | constructor injection wired in `main` / app factory | python-dependency-injector for large services | FastAPI `Depends` at the edge only |
| csharp-dotnet | `Microsoft.Extensions.DependencyInjection` | none needed | register in `Program.cs`; validate the container at startup |

## Evidence

Fowler's original article, Seemann's service-locator anti-pattern, the Android
DI guide, Koin's compile-time verification, swift-dependencies' test values,
injectable over get_it. [../evidence.md](../evidence.md), D13.
