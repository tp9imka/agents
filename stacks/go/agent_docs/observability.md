# Observability - Go

Rules in `CONSTITUTION.md` article IV.

## The canonical event

`pkg/observability/event.go`:

```go
type CanonicalEvent struct {
    Name       string            // "http.request", "job.reconcile", "orders.place"
    TraceID    string
    SpanID     string
    Outcome    Outcome           // OK, Error, Cancelled
    ErrorType  string            // errors.As target name or code; never the message
    DurationMs int64
    UserID     string            // hashed
    Attrs      map[string]any    // http.route, http.response.status_code, order.id, ...
}
```

`pkg/observability/middleware.go` wraps every HTTP and gRPC handler and the
worker's job runner: it starts a span, stores an event builder in the
context, and in `defer` fills outcome, error type and duration and emits the
event as one `slog` record with the span's attributes. Handlers and use cases
add fields with `observability.Add(ctx, "order.id", id)`.

Tests: `middleware_test.go` asserts one event with `outcome=ok` for a 200 and
`outcome=error` plus `error.type` for a failing handler; the same for gRPC and jobs.

## Logger

`pkg/observability/logger.go` builds `slog.New(slog.NewJSONHandler(os.Stdout, opts))`
with the redacting handler wrapped around it, and puts a request-scoped logger
in the context:

```go
log := observability.Logger(ctx)           // carries trace_id, span_id, request attrs
log.Info("order placed", "order.id", id)
log.Error("place failed", "error.type", errType, "err", err)
```

Levels: `Debug` (dev), `Info`, `Warn` (only if actionable), `Error` with
`error.type`. Libraries return errors; the top of the request logs once.
Forbidden calls in `.golangci.yml`:

```yaml
linters-settings:
  forbidigo:
    forbid:
      - p: ^fmt\.Print.*$ ;   msg: use observability.Logger(ctx)
      - p: ^log\.(Print|Fatal|Panic).*$
      - p: ^println$
      - p: ^time\.Now$ ;      msg: inject clock.Clock
        pkg: ^internal/.*/app$
```

## Privacy

- Never log tokens, passwords, message bodies or free text; ids are fine.
- `pkg/observability/redact.go` is a `slog.Handler` that replaces values of keys matching `password|token|secret|body|content|authorization`.
- Request and response bodies are never logged; sizes are.

## Usage statistics

```go
// pkg/analytics/events.go
func CheckoutStarted(itemCount int) Event { return Event{Name: "checkout_started", Props: P{"item_count": itemCount}} } // owner: growth
func OrderPlaced(orderID string, amountMinor int64) Event { ... }
```

`analytics.Track(ctx, ev Event)` is the only sink; `Event` has an unexported
constructor field so callers must use the catalogue. Names are `object_action`
snake_case, never dynamic. Consent is checked in `Track`.

## Performance

- `pkg/observability/otel.go`: OTel SDK with OTLP exporter, `otelhttp` on the
  server and client, `otelgrpc`, `otelpgx`; resource attributes
  `service.name`, `service.version`, `deployment.environment`.
- Golden signals per route from the middleware: latency histogram, request
  count, error count, in-flight gauge (`otel` metrics).
- `net/http/pprof` on the admin port; `runtime/metrics` exported.
- Sampling: parent-based 10%, errors always; retention default 30 days; both in `otel.go`.
