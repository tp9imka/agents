# Observability - Kotlin / Android

Read before adding a screen, a use case, a network call, a log line or an
analytics event. Rules in `CONSTITUTION.md` article IV.

## The canonical event

`core/observability/src/main/kotlin/com/acme/observability/CanonicalEvent.kt`:

```kotlin
data class CanonicalEvent(
    val name: String,              // "orders.create", "screen.checkout"
    val traceId: String,
    val spanId: String,
    val outcome: Outcome,          // Ok, Error, Cancelled
    val errorType: String? = null, // exception class or error code, never the message
    val durationMs: Long,
    val userId: String? = null,    // hashed
    val sessionId: String,
    val attributes: Map<String, Any> = emptyMap(), // order.id, feature_flag.*, ...
)
```

Emitted by:

- `ObservedUseCase<I, O>`: every use case extends it; `invoke` opens a span,
  runs the body, and emits the event in `finally`.
- `ScreenObserver`: a `DisposableEffect` installed by `AppScaffold` for every
  route; emits `screen.<route>` with time on screen.
- `OkHttp` interceptor from the OTel Android agent for network spans.

Test per feature: `CanonicalEventTest` runs the use case with a `FakeTracker`
and asserts name, outcome and `durationMs > 0` for the success and the failure path.

## Logger

`core/observability/Logger` wraps the OTel logs bridge and `Log` in debug:

```kotlin
interface Logger {
    fun debug(msg: String, vararg fields: Pair<String, Any?>)
    fun info(msg: String, vararg fields: Pair<String, Any?>)
    fun error(msg: String, error: Throwable?, vararg fields: Pair<String, Any?>)
}
```

Obtain it by injection (`@Inject lateinit` is forbidden; use the constructor).
`android.util.Log.*`, `println`, `Timber.*` are forbidden by detekt:

```yaml
# config/detekt/detekt.yml
style:
  ForbiddenMethodCall:
    active: true
    methods:
      - value: 'android.util.Log.d'
      - value: 'android.util.Log.i'
      - value: 'android.util.Log.w'
      - value: 'android.util.Log.e'
      - value: 'kotlin.io.println'
      - value: 'java.lang.System.currentTimeMillis'
```

Release builds strip `debug` calls with `-assumenosideeffects` in
`app/proguard-rules.pro`.

## Privacy

- Never log tokens, passwords, message bodies, addresses or free-text input.
  User and order ids are allowed. See `android-log-info-disclosure` in the
  evidence for why device logs count as exposure.
- `OtelExporterConfig` applies an attribute processor that drops keys matching
  `password|token|secret|body|content` before export.
- Sealed-class payloads with sensitive fields override `toString()` to the case name.

## Usage statistics

`core/analytics/AnalyticsEvent.kt` is the catalogue:

```kotlin
sealed class AnalyticsEvent(val name: String) {
    data class CheckoutStarted(val itemCount: Int) : AnalyticsEvent("checkout_started")
    data class OrderPlaced(val orderId: String, val amountMinor: Long) : AnalyticsEvent("order_placed")
    // add an entry with an owner and a reason in the KDoc; delete events nobody reads
}
```

`Tracker.track(event: AnalyticsEvent)` is the only sink. A detekt custom rule
(`AnalyticsCatalogueOnly`) fails on `track("...")` with a string. Names are
`object_action`, snake_case, letters, digits and underscores, never dynamic.
Consent is checked in `Tracker` before the first event.

## Performance

- The OpenTelemetry Android agent (`io.opentelemetry.android:android-agent`)
  is initialised in `App.onCreate()` via `core/observability/OtelSetup.kt`:
  cold and warm start, time to initial display, slow and frozen frames, ANRs,
  crash reporting, OkHttp spans, session id.
- Custom spans for heavy work: `tracer.spanBuilder("orders.sync").startSpan()`
  inside `ObservedUseCase`, so they carry the trace id.
- Perfetto (`Trace.beginSection`) for local investigation of startup and jank.
- Sampling: `info` events at 10%, errors at 100%; retention default 30 days;
  both set in `OtelExporterConfig`.
