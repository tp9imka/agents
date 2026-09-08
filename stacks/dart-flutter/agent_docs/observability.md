# Observability - Dart / Flutter

Rules in `CONSTITUTION.md` article IV.

## The canonical event

`packages/core/observability/lib/src/canonical_event.dart`:

```dart
class CanonicalEvent {
  final String name;            // 'orders.place', 'screen.checkout'
  final String traceId, spanId;
  final Outcome outcome;        // ok, error, cancelled
  final String? errorType;      // type or code, never the message
  final int durationMs;
  final String? userId;         // hashed
  final String sessionId;
  final Map<String, Object> attributes;
}
```

Emitted by `ObservedUseCase<I, O>` (every use case extends it; `call` opens a
span, runs `execute`, emits in `finally`) and by `ObservedRoute`, a
`NavigatorObserver` registered in `router.dart` for every route. dio spans come
from the `ObservabilityInterceptor` in `core/network`.

Test per feature: `canonical_event_test.dart` runs the use case with
`FakeTracker` and asserts name, outcome and `durationMs > 0` on success and failure.

## Logger

`packages/core/observability/lib/src/log.dart` wraps `package:logging` and
forwards to the Sentry logger in release:

```dart
final log = Log('orders');
log.info('order placed', {'order.id': id});
log.severe('place failed', error: e, fields: {'error.type': e.runtimeType.toString()});
```

Levels: `fine` (dev only, stripped in release), `info`, `warning` (must be
actionable), `severe` with `error.type`. `print`, `debugPrint`,
`developer.log` and `stdout.writeln` are banned:

```yaml
# analysis_options.yaml (root, inherited by every package)
include: package:very_good_analysis/analysis_options.yaml
linter:
  rules:
    avoid_print: true
custom_lint:
  rules:
    - no_debug_print
    - no_datetime_now
    - analytics_catalogue_only
```

The three custom rules live in `packages/core/lints`.

## Privacy

- Never log tokens, message bodies, addresses or free text; ids are fine.
- `SentryFlutterOptions.beforeSend` and the OTel span processor in
  `otel_config.dart` drop attributes matching `password|token|secret|body|content`.
- Freezed classes with secret fields override `toString` to the type name.

## Usage statistics

```dart
sealed class AnalyticsEvent {
  const AnalyticsEvent(this.name);
  final String name;
}
/// owner: growth - funnel step 1
final class CheckoutStarted extends AnalyticsEvent { const CheckoutStarted(this.itemCount) : super('checkout_started'); final int itemCount; }
```

`Tracker.track(AnalyticsEvent)` is the only sink and checks consent first.
`track('...')` with a string fails `analytics_catalogue_only`. Names are
`object_action` snake_case, never dynamic.

## Performance

- Sentry Flutter (`SentryFlutter.init` in `main_*.dart`): app start, slow and
  frozen frames, screen load, navigation spans (`SentryNavigatorObserver`), TTID/TTFD.
- opentelemetry-dart: spans from `ObservedUseCase` exported OTLP; logs are not
  implemented in that SDK yet, so structured logs go through Sentry logs.
- Flutter DevTools timeline for local jank investigation; `Timeline.startSync`
  markers inside `ObservedUseCase` for heavy work.
- Sampling: `tracesSampleRate 0.1`, errors 100%; retention default 30 days;
  both in `otel_config.dart` / `SentryFlutterOptions`.
