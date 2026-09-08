# Architecture - Swift / iOS

Read when adding a package, a feature, a port or a dependency key.

## Package map

```
App/                                   the app target: AppDependencies.swift (composition root), AppNavigation.swift, App.swift
Packages/<Feature>/Package.swift       targets: <Feature>API, <Feature>, <Feature>Tests
  Sources/<Feature>API/                destinations, public events, small models other features may use
  Sources/<Feature>/Domain/            entities, value types, domain services - imports Foundation only
  Sources/<Feature>/Application/       use cases, ports (protocols owned here)
  Sources/<Feature>/Adapters/          HTTP clients, persistence, SDK wrappers implementing the ports
  Sources/<Feature>/UI/                SwiftUI views, the @Observable screen models, State and Event types
  Tests/<Feature>Tests/                swift-testing suites mirroring Sources
Packages/Observability/                CanonicalEvent, Log, MetricsSubscriber, OtelConfig
Packages/Analytics/                    AnalyticsEvent enum and the Tracker port
Packages/Networking/, Packages/Persistence/   shared infrastructure, no feature knowledge
Packages/DesignSystem/                 theme, tokens, components, previews
Packages/TestSupport/                  fakes for shared ports, snapshot helpers
Scripts/check-layers.sh                the import gate
Scripts/coverage-gate.sh               xccov => fail under 100
```

## Layer rules

- `Domain` imports `Foundation` only.
- `Application` imports `Domain` and declares ports as protocols; no `SwiftUI`, `SwiftData`, `URLSession`.
- `Adapters` implement ports; they never import `UI`.
- `UI` imports `Application` and `Domain`; never `Adapters`.
- A feature imports other features through `<Feature>API` only; `App` is the only target that imports feature implementation targets.

`Scripts/check-layers.sh` (run by `make check`) greps `import` lines per
directory and fails on a violation. Add a line to the script when you add a rule.

## Dependencies

swift-dependencies keys in the package that owns the port:

```swift
struct OrdersClient: Sendable {
    var fetch: @Sendable (UserID) async throws -> [Order]
    var place: @Sendable (Cart) async throws -> OrderID
}
extension OrdersClient: DependencyKey {
    static let liveValue = OrdersClient.http(URLSessionTransport())
    static let testValue = OrdersClient(fetch: unimplemented("OrdersClient.fetch"),
                                        place: unimplemented("OrdersClient.place"))
}
extension DependencyValues { var orders: OrdersClient { get { self[OrdersClient.self] } set { self[OrdersClient.self] = newValue } } }
```

`liveValue` assignments that need app-level wiring live in
`App/AppDependencies.swift`. `DependencyGraphTests` resolves every key once so a
missing live value fails `make check`.

## Screen models

```swift
@Observable @MainActor
final class OrderModel {
    struct State: Equatable { var items: [Item] = []; var isPlacing = false; var error: OrderError? }
    enum Event { case appeared, placeTapped, retryTapped }
    private(set) var state = State()
    @ObservationIgnored @Dependency(\.placeOrder) private var placeOrder
    func send(_ event: Event) async { /* reduce, call use cases, mutate state */ }
}
```

Views call `model.send(.placeTapped)` and render `model.state`. Transition
tests drive `send` and assert `state`. TCA is the documented alternative when a
feature needs composable reducers and exhaustive `TestStore` assertions.

## Modern API table

| Use | Not |
|---|---|
| `@Observable` + `@State` / `@Bindable` | `ObservableObject`, `@StateObject`, `@ObservedObject` |
| `NavigationStack` + `navigationDestination(for:)` | `NavigationView` |
| `Text(value, format: .number.precision(...))`, `date.formatted(...)` | `String(format:)`, `DateFormatter` |
| async/await, `Task`, actors | GCD, completion handlers |
| `foregroundStyle`, `clipShape(.rect(cornerRadius:))`, `Tab` | `foregroundColor`, `cornerRadius`, `tabItem` |
| `containerRelativeFrame`, `visualEffect` | `GeometryReader` unless nothing else works |
| `Task.sleep(for:)` | `Task.sleep(nanoseconds:)` |
| `localizedStandardContains` for user text | `contains` |

Encoded as SwiftLint custom rules in `.swiftlint.yml`; the model's Swift is
older than this table, so the rules are the enforcement.

## Size and placement

- A screen model above 250 lines or a use case above 120 lines is split.
- Shared code moves to a `Packages/*` infrastructure package only when a second feature needs it.
