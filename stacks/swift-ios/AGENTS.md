# AGENTS.md - <Project> (Swift / iOS)

<Project> is an iOS app: Swift <6.x> with strict concurrency, SwiftUI, iOS
<17>+, one Swift package per feature and per layer under `Packages/`, the app
target in `App/`. State with `@Observable` models per screen (TCA is the
documented alternative), dependencies via swift-dependencies, SwiftData or
GRDB for persistence, `URLSession` behind a port. The seven articles of
`CONSTITUTION.md` apply; each names its gate below.

## Commands

- Setup: Xcode from `.xcode-version`; `make bootstrap` installs SwiftLint, SwiftFormat, Muter and the git hooks (`mise` or Homebrew, see `Makefile`).
- Check (the CI gate): `make check` - `swiftformat --lint`, `swiftlint --strict`, the layer script, `xcodebuild test` for every package, the coverage gate at 100%, snapshot verification.
- Build: `xcodebuild build -scheme App -destination 'platform=iOS Simulator,name=iPhone 16'`
- Test all packages: `make test`
- Test one package: `swift test --package-path Packages/Orders`
- Test one test: `swift test --package-path Packages/Orders --filter OrderModelTests/placesOrderWhenCartIsValid`
- Format and lint: `swiftformat . && swiftlint --fix --strict`
- Coverage report: `make coverage` => `build/coverage/index.html` (from `xccov --json`).
- Iterate with `swift test --package-path` on the package you changed; run `make check` before declaring done.

## Architecture

- Feature-first packages: `Packages/<Feature>` exposes targets `<Feature>API` (contracts, navigation destinations, events) and `<Feature>` (domain, use cases, ports, adapters, views). Other features import `<Feature>API` only. Gate: the compiler (target dependencies in `Package.swift`) plus `Scripts/check-layers.sh` in `make check`.
- Dependency rule inside a feature: `Domain` <= `Application` <= `Adapters`/`UI`. `Domain` imports only `Foundation`; no SwiftUI, SwiftData or `URLSession` there. Gate: `Scripts/check-layers.sh` greps imports per target.
- DI: swift-dependencies. Every dependency is a `DependencyKey` with `liveValue` and a `testValue` that is unimplemented, so unstubbed access fails tests. Wiring happens in `App/AppDependencies.swift` only. Gate: `DependencyGraphTests` resolves every key.
- UI: one `@Observable @MainActor` model per screen owning an immutable `State`; views render and send events; side effects go through use cases. Gate: SwiftLint custom rule `no_state_object_mutation_in_view`.
- Modern API only: `Observable` not `ObservableObject`, `NavigationStack` not `NavigationView`, `FormatStyle` not `Formatter`, async/await not callbacks or GCD. Gate: SwiftLint `deprecated_api` custom rules in `.swiftlint.yml`.
- Layout and rules in full: `agent_docs/architecture.md`.

## Testing

- Test-first: the failing test comes first; a change whose tests pass with it stashed is not done. Gate: review runs `git stash && make test` on the diff; no Swift TDD hook exists yet.
- Coverage: `Scripts/coverage-gate.sh` reads `xccov --json` and fails below 100% regions per package. Exclusions: none by config; a branch that cannot be reached is removed or the file says why in a comment above it.
- Framework: swift-testing (`@Test`, `#expect`, `@Suite`, parameterised `@Test(arguments:)`); XCTest only for UI tests. Fakes for own ports live in `Packages/TestSupport`.
- Snapshots: swift-snapshot-testing per screen state; goldens recorded in CI on `main`, never from a workstation. Gate: `make check` runs them.
- Mutation: `muter` on `Packages/*` nightly (`.github/workflows/nightly.yml`); a score under 80% fails.
- Time and randomness through `@Dependency(\.date)` and `@Dependency(\.uuid)`; `Date()` and `UUID()` in package sources are forbidden. Gate: SwiftLint `no_direct_date`.
- Recipes: `agent_docs/testing.md`.

## Observability

- Every screen visit and every use-case call emits one canonical event through `Packages/Observability` (`CanonicalEvent`: `event.name`, `trace_id`, `outcome`, `error.type`, `duration_ms`, `user.id`, business fields). `ObservedUseCase` and the `.observedScreen()` modifier emit it in `defer`; feature code cannot skip it. Gate: `CanonicalEventTests` per feature.
- Logging: `os.Logger` instances come from `Packages/Observability/Log.swift` (one subsystem, a category per module). `print`, `NSLog` and `debugPrint` are forbidden. Gate: SwiftLint `no_print`.
- Levels: `debug` (memory only), `info`, `notice` (default, persisted), `error` with `error.type`, `fault` for bugs. A `notice` must be worth persisting.
- Privacy: interpolated values are private by default; mark only ids `privacy: .public`. Never log tokens, message bodies or free text. Enums with secret payloads log the case name only.
- Usage events: `Packages/Analytics/AnalyticsEvent.swift` (an enum) is the catalogue; names `object_action` in snake_case; `Tracker.track(_:)` takes the enum only. Gate: SwiftLint `analytics_catalogue_only`.
- Performance: MetricKit payloads (launch, hangs, crashes) collected in `MetricsSubscriber`; signposts from `ObservedUseCase` for spans; OpenTelemetry Swift exports spans and logs; targets: first frame under 400 ms. Sampling and retention in `OtelConfig.swift`.
- Setup and fields: `agent_docs/observability.md`.

## Boundaries

- Always: run the package's tests after each change and `make check` before saying done; add a `check-layers.sh` rule or a SwiftLint rule when you add an architectural rule; put new code in a `Packages/<Feature>` target, never in `App/` except wiring and navigation.
- Ask first: adding a package dependency in `Package.swift`; raising the deployment target or the Swift tools version; changing a `<Feature>API` contract; touching `Scripts/` or `.github/workflows/`.
- Never: commit secrets or `*.xcconfig` with keys (use `Config/Secrets.xcconfig.example`); edit `Localizable.xcstrings` by hand (it is generated - change the source strings); disable, delete or weaken a failing test (ask); use `print` or `NSLog` (use `Log.<category>`); use `DispatchQueue`, `ObservableObject`, `NavigationView` or `DateFormatter` (use the modern API in `agent_docs/architecture.md`); force-unwrap or `try!` outside tests (use `guard` and typed errors).

## Where to look

- `agent_docs/architecture.md` - package map, layer script, dependency keys, modern-API table
- `agent_docs/testing.md` - swift-testing patterns, fakes, snapshots, the coverage script, Muter
- `agent_docs/observability.md` - canonical event, logger, catalogue, MetricKit, OTel export, privacy
- `agent_docs/gates.md` - what `make check` runs, CI, hooks
- Exemplars: `Packages/Orders/Sources/Orders/UI/OrderModel.swift`, `Packages/Orders/Sources/Orders/Adapters/OrdersHTTPClient.swift`, `Packages/Orders/Tests/OrdersTests/OrderModelTests.swift`
- Legacy: none. When a legacy target appears, list it here and do not copy its patterns.

## Maintaining this file

- Add a line only after an observed failure, then re-run the task without and with the line and keep it only if the outcome changed. Every rule names its gate or its reason. Revisit after model releases. Stay under 150 lines.
