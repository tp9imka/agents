# Observability - Python

Rules in `CONSTITUTION.md` article IV.

## The canonical event

`src/<project>/observability/event.py`:

```python
@dataclass(frozen=True, slots=True)
class CanonicalEvent:
    name: str                    # "http.request", "orders.place"
    trace_id: str
    span_id: str
    outcome: Outcome             # OK, ERROR, CANCELLED
    error_type: str | None       # class name or code, never the message
    duration_ms: int
    user_id: str | None          # hashed
    attrs: Mapping[str, object]
```

`observability/middleware.py` is a pure ASGI middleware: it starts the span,
binds `trace_id` and request attributes into structlog contextvars, and in a
`finally` emits the event as one structlog record. Use cases add fields with
`observe.add(order_id=...)`; jobs use `observed_job("name")`.

Tests: `tests/observability/test_canonical_event.py` calls a 200 route and a
raising route through `ASGITransport` and asserts one event each with
`outcome` and `duration_ms` using `capture_logs()`.

## Logger

`observability/logging.py` configures structlog once (called from `app/main.py`):

```python
structlog.configure(processors=[
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
    redact_sensitive,                       # drops password|token|secret|body|content|authorization
    structlog.processors.dict_tracebacks,
    structlog.processors.JSONRenderer(),
])
log = structlog.get_logger()
log.info("order placed", order_id=str(order.id))
log.error("place failed", error_type=type(exc).__name__)
```

Levels: `debug` (dev), `info`, `warning` only if actionable, `error` with
`error_type`. `print` and stdlib `logging` outside this module are banned:

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "B", "T20", "DTZ", "ASYNC", "PL", "RUF"]
[tool.ruff.lint.flake8-tidy-imports.banned-api]
"logging.getLogger".msg = "use structlog.get_logger() from <project>.observability"
"datetime.datetime.now".msg = "inject Clock"
"time.time".msg = "inject Clock"
"random.random".msg = "inject random.Random"
```

## Privacy

- Never log tokens, message bodies or free text; ids are fine.
- `redact_sensitive` replaces values for the key list above; request bodies are never logged, sizes are.
- Secret settings use `pydantic.SecretStr`, which never renders in `repr`.

## Usage statistics

```python
# analytics/events.py
@dataclass(frozen=True, slots=True)
class CheckoutStarted:           # owner: growth - funnel step 1
    name: ClassVar[str] = "checkout_started"
    item_count: int

def track(event: AnalyticsEvent) -> None: ...   # AnalyticsEvent is a Union of the dataclasses; checks consent
```

Names are `object_action` snake_case, never dynamic; mypy rejects anything
outside the union; the vendor SDK is importable only from `analytics/`
(`banned-api`).

## Performance

- `observability/otel.py`: OpenTelemetry Python SDK with the OTLP exporter,
  `FastAPIInstrumentor`, `SQLAlchemyInstrumentor`, `HTTPXClientInstrumentor`;
  resource attributes `service.name`, `service.version`, `deployment.environment`.
- The middleware records latency histogram, request count, error count and
  in-flight gauge per route (golden signals) through the OTel metrics API.
- `py-spy` for profiling; `uvicorn --access-log` off (the canonical event replaces it).
- Sampling: parent-based 10%, errors always; retention default 30 days; both in `observability/config.py`.
