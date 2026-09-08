# Observability from day one

Constitution article IV. Written logging instructions fail two thirds of the
time, so each rule here is paired with a structural enforcer.

## The canonical event

Every unit of work emits exactly one structured event when it ends, in a
finally block, whatever happened. Unit of work: an HTTP request, a job, a
message, a CLI command, a screen visit, a user action that hits a port.

Required fields (OpenTelemetry names where they exist):

| Field | Example |
|---|---|
| `event.name` | `orders.create`, `screen.checkout` |
| `trace_id`, `span_id` | from the tracer; propagated with W3C `traceparent` |
| `service.name`, `service.version`, `deployment.environment` | resource attributes |
| `outcome` | `ok`, `error`, `cancelled` |
| `error.type` | exception class or error code; never the message alone |
| `duration_ms` | end minus start |
| identity | `user.id` (hashed if PII rules require), `session.id` |
| business fields | `order.id`, `feature_flag.*`, whatever the domain needs to debug |
| `commit.sha` | build id |

In OTel terms this is one span per unit of work with these attributes; logs
inside the unit of work carry the same `trace_id`. Metrics are derived from
events, not emitted separately unless a dashboard needs a counter.

Enforcer: a middleware, interceptor, or base class emits the event so feature
code cannot forget it, plus one test per transport that asserts the event was
emitted with `outcome` and `duration_ms`.

## The logger

- One logger per module, obtained through the DI graph or a module-scoped
  factory. Structured key-value fields, never string interpolation.
- Nothing calls `print`, `println`, `console.*`, `NSLog`, `Log.d` or `fmt.Println`
  outside the logger implementation. Enforcer: a lint rule in the check command.
- Levels: `debug` for developers (off in release), `info` for operators,
  `error` for handled failures with `error.type`. A `warn` must be actionable
  or it is `info`. Libraries return errors; they do not log them.
- Tests assert on structured events, not on log text.

| Stack | Logger | Lint |
|---|---|---|
| kotlin-android | `Logger`/Timber facade over OSLog-equivalent `Log`, OTel Android agent | detekt `ForbiddenMethodCall` on `android.util.Log`, `println` |
| java-spring | SLF4J with Spring Boot structured logging (ECS), Micrometer tracing | ArchUnit rule: no `System.out` |
| swift-ios | `os.Logger` per subsystem/category; OTel Swift for export | SwiftLint custom rule on `print`, `NSLog` |
| dart-flutter | `logging` package or Sentry logger behind a facade | `avoid_print` lint |
| go | `log/slog` JSON handler; `slog.With` for request attributes | `forbidigo` on `fmt.Print*`, `log.Print*` |
| rust | `tracing` + `tracing-subscriber` JSON; `#[instrument]` on entry points | clippy `print_stdout`, `print_stderr` deny |
| typescript-web | pino (server), a thin facade in the browser | eslint `no-console` |
| python | structlog, JSON renderer | ruff `T201` (print) |
| csharp-dotnet | `ILogger<T>` with Serilog or OTel exporter, message templates | analyzer CA2254; ban `Console.Write*` |

## Privacy

- No secrets, tokens, passwords, message bodies or free-text user content in
  logs or events. Identifiers are fine when the platform says so.
- Interpolated values are private by default (OSLog) or redacted by a list
  (pino `redact`, OTel attribute processors). Release builds strip debug logs.
- Enum payloads with secrets log the case name only.

## Usage statistics

- A typed event catalogue in code (an enum or generated client) is the only
  way to send an analytics event. No string event names at call sites.
- Naming: `object_action` in snake_case (`checkout_started`), letters, digits
  and underscores only, never dynamic. Properties in snake_case.
- Each event has an owner and a reason in the catalogue. Events nobody reads
  are deleted.
- Consent and opt-out are honoured before the first event.

## Performance traces

| Platform | Emit from the first build |
|---|---|
| server | the four golden signals per endpoint: latency, traffic, errors, saturation |
| android | cold and warm start, time to initial display, slow and frozen frames, ANRs; spans visible in Perfetto |
| ios | launch time, time to first frame (target under 400 ms), hangs, MetricKit payloads, signposts for spans |
| flutter | app start, frame build and raster times, first meaningful paint |
| web | LCP, INP, CLS, plus User Timing marks for app-specific steps |

Spans for outbound calls, database queries and heavy work carry the trace id.

## Cost

Sample high-volume events at the edge; keep errors unsampled. Aggregate
periodic polls instead of logging each. State the retention default in
`agent_docs/observability.md`.

## Evidence

Stripe canonical log lines, the wide-events guides, OTel semantic conventions
and the logs data model, the SRE golden signals, Sentry mobile vitals,
web.dev metrics, Segment and Firebase naming, Element X and Android privacy
rules, Cloudflare's logger rule, Airflow's structured-assertion rule, and the
study of agent logging behaviour. [../evidence.md](../evidence.md), D11.
