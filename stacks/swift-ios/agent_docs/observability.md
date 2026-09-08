# Observability - Swift / iOS

Rules in `CONSTITUTION.md` article IV; this page is the setup.

## The canonical event

`Packages/Observability/Sources/Observability/CanonicalEvent.swift`:

```swift
struct CanonicalEvent: Sendable {
    var name: String            // "orders.place", "screen.checkout"
    var traceId: String, spanId: String
    var outcome: Outcome        // .ok, .error, .cancelled
    var errorType: String?      // type name or code, never the message
    var durationMs: Int
    var userId: String?         // hashed
    var sessionId: String
    var attributes: [String: AttributeValue]
}
```

Emitted by `ObservedUseCase` (every use case is wrapped: opens a span, runs,
emits in `defer`) and by the `.observedScreen("checkout")` view modifier
installed on every destination in `App/AppNavigation.swift`. Network spans
come from `URLSessionInstrumentation` in OpenTelemetry Swift.

Test per feature: `CanonicalEventTests` runs the use case with `Tracker.fake`
and checks name, outcome and `durationMs > 0` on success and on failure.

## Logger

`Packages/Observability/Sources/Observability/Log.swift`:

```swift
enum Log {
    static let subsystem = Bundle.main.bundleIdentifier!
    static let orders = Logger(subsystem: subsystem, category: "orders")
    static let network = Logger(subsystem: subsystem, category: "network")
}
Log.orders.info("order placed id=\(order.id, privacy: .public)")
Log.orders.error("place failed type=\(String(describing: type(of: error)), privacy: .public)")
```

Levels: `debug` stays in memory, `info` is collected on demand, `notice`
persists (the default, use it for what an operator needs), `error`, `fault`.
`print`, `NSLog`, `debugPrint` are banned:

```yaml
# .swiftlint.yml
custom_rules:
  no_print:
    regex: '^\s*(print|NSLog|debugPrint)\('
    message: "Use Log.<category> (Packages/Observability)"
    severity: error
  analytics_catalogue_only:
    regex: 'track\("'
    message: "Pass an AnalyticsEvent case, not a string"
    severity: error
  no_direct_date:
    included: "Packages/.*/Sources/.*"
    regex: '\b(Date\(\)|UUID\(\))'
    message: "Use @Dependency(\\.date) / (\\.uuid)"
    severity: error
```

## Privacy

- Interpolated values are private by default in OSLog; mark ids `privacy: .public`, nothing else.
- Never log tokens, message bodies, addresses or free text. Enums carrying secrets implement `CustomStringConvertible` to print the case name.
- `OtelConfig` installs an attribute processor dropping keys matching `password|token|secret|body|content`.

## Usage statistics

```swift
enum AnalyticsEvent {
    case checkoutStarted(itemCount: Int)      // owner: growth, reason: funnel step 1
    case orderPlaced(orderId: String, amountMinor: Int)
    var name: String { switch self { case .checkoutStarted: "checkout_started"; case .orderPlaced: "order_placed" } }
}
```

`Tracker.track(_ event: AnalyticsEvent)` is the only sink; consent is checked
inside. Names are `object_action` snake_case, never dynamic.

## Performance

- `MetricsSubscriber` (in `Packages/Observability`) receives MetricKit
  payloads: launch time, hang rate, crash diagnostics, memory. Registered in `App.init`.
- Signposts: `ObservedUseCase` wraps the span in `os_signpost` so it appears
  in Instruments; OpenTelemetry Swift `SignPostIntegration` bridges the same spans.
- Targets: first frame under 400 ms, no hangs over 250 ms in the top three
  screens; checked on the nightly device run.
- Export: OpenTelemetry Swift OTLP exporter configured in `OtelConfig.swift`;
  sampling 10% of `info` events, 100% of errors; retention default 30 days.
