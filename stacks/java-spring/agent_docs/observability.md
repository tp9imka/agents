# Observability - Java or Kotlin / Spring Boot

Rules in `CONSTITUTION.md` article IV.

## The canonical event

`com.acme.observability.CanonicalEvent` (a record): `name`, `traceId`,
`spanId`, `outcome` (OK, ERROR, CANCELLED), `errorType`, `durationMs`,
`userId` (hashed), `attributes` (map).

`CanonicalEventFilter` is a `OncePerRequestFilter` ordered first: it reads the
current `Observation` (Micrometer) for trace and span ids, exposes
`Observe.add(key, value)` through a request-scoped holder, and emits the event
in `finally` as one structured log line with all fields. `ObservedListener`
wraps message listeners; scheduled jobs use `Observe.job("name", runnable)`.

Tests: `CanonicalEventTest` with `@WebMvcTest` and `OutputCaptureExtension`
asserts one JSON event with `outcome=OK` for a 200 and `outcome=ERROR` plus
`error.type` for a throwing controller.

## Logging

`application.yml`:

```yaml
logging:
  structured:
    format:
      console: ecs
  level:
    root: INFO
management:
  tracing:
    sampling:
      probability: 0.1
```

Loggers: `private static final Logger log = LoggerFactory.getLogger(PlaceOrder.class);`
with key-value pairs (`log.atInfo().addKeyValue("order.id", id).log("order placed")`).
MDC carries `traceId` and `spanId` automatically from Micrometer tracing.
Levels: `DEBUG` (dev), `INFO`, `WARN` only if actionable, `ERROR` with
`error.type`. `System.out`, `System.err` and `printStackTrace` fail
ArchUnit and Checkstyle (`Regexp` check with `format="System\.(out|err)"`).

## Privacy

- Never log tokens, message bodies or free text; ids are fine.
- `logback-spring.xml` wraps the ECS encoder with a masking converter for
  `password|token|secret|body|content|authorization` values.
- Request bodies are never logged; `CommonsRequestLoggingFilter` is not used.

## Usage statistics

```java
public sealed interface AnalyticsEvent permits CheckoutStarted, OrderPlaced {
    String name();
}
/** owner: growth - funnel step 1 */
public record CheckoutStarted(int itemCount) implements AnalyticsEvent { public String name() { return "checkout_started"; } }
```

`Tracker.track(AnalyticsEvent)` is the only sink and checks consent. Names are
`object_action` snake_case, never dynamic. ArchUnit forbids the vendor SDK
outside `com.acme.analytics`.

## Performance

- Micrometer Observation API with `micrometer-tracing-bridge-otel` and the
  OTLP exporter; resource attributes `service.name`, `service.version`,
  `deployment.environment` from `management.opentelemetry.resource-attributes`.
- Golden signals per endpoint from `http.server.requests` (latency histogram
  with percentiles, count, errors) and `tomcat.threads` for saturation; JDBC
  spans via `datasource-micrometer`; messaging spans via the Modulith
  observability starter.
- JFR (`-XX:StartFlightRecording`) for profiling in staging; `management`
  endpoints on a separate port.
- Sampling 10%, errors always through a custom `Sampler` bean; retention
  default 30 days; both in `ObservabilityConfig`.
