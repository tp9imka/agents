# Observability - Rust

Rules in `CONSTITUTION.md` article IV.

## The canonical event

`crates/infra-observability/src/event.rs`:

```rust
pub struct CanonicalEvent {
    pub name: &'static str,     // "http.request", "orders.place"
    pub trace_id: String, pub span_id: String,
    pub outcome: Outcome,       // Ok, Error, Cancelled
    pub error_type: Option<&'static str>,
    pub duration_ms: u64,
    pub user_id: Option<String>, // hashed
    pub attrs: Vec<(&'static str, Value)>,
}
```

`infra-observability/src/layer.rs` is a `tower::Layer` on the Axum router:
it opens the request span, holds an `EventBuilder` in extensions, and a
`Drop` guard emits the event as one structured `tracing::info!` (or `error!`)
with the fields above, whatever the outcome. Use cases are
`#[tracing::instrument(skip_all, fields(...))]` so their spans nest under the
request span; jobs use `observed_job("name", fut)`.

Tests: `layer_test.rs` captures the subscriber with `tracing-test` and asserts
one event per request with `outcome` and `duration_ms`, on 200 and on 500.

## Subscriber

`crates/infra-observability/src/subscriber.rs` installs
`tracing_subscriber::registry()` with a JSON fmt layer (`.json().flatten_event(true)`),
`EnvFilter` from `RUST_LOG`, the redaction layer, and
`tracing_opentelemetry::layer()` with an OTLP exporter.

```rust
tracing::info!(order.id = %id, "order placed");
tracing::error!(error.type = %kind, error = %e, "place failed");
```

Forbidden in `src/`: `println!`, `eprintln!`, `dbg!`, the `log` crate.
`Cargo.toml` workspace lints:

```toml
[workspace.lints.clippy]
print_stdout = "deny"
print_stderr = "deny"
dbg_macro = "deny"
unwrap_used = "deny"
expect_used = "deny"
```

and `deny.toml` bans the `log` crate. Levels: `debug` (dev), `info`, `warn`
only if actionable, `error` with `error.type`.

## Privacy

- Never log tokens, message bodies or free text; ids are fine.
- The redaction layer replaces values of fields named `password`, `token`,
  `secret`, `body`, `content`, `authorization`.
- Types holding secrets implement `Debug` manually (`secrecy::Secret`).

## Usage statistics

```rust
// infra-analytics/src/events.rs
pub enum Event { CheckoutStarted { item_count: u32 }, OrderPlaced { order_id: OrderId, amount_minor: i64 } }
impl Event { pub fn name(&self) -> &'static str { match self { Self::CheckoutStarted{..} => "checkout_started", ... } } }
```

`Tracker::track(&self, ev: Event)` is the only sink and checks consent.
Names are `object_action` snake_case, never dynamic; an owner and reason
comment sits above each variant.

## Performance

- `tracing-opentelemetry` exports spans; `opentelemetry-otlp` with resource
  attributes `service.name`, `service.version`, `deployment.environment`.
- The Axum layer records latency histogram, request count, error count and
  in-flight gauge per route through the `metrics` crate and the Prometheus exporter.
- `tokio-console` behind a `console` feature in dev; `cargo flamegraph` for CPU.
- Sampling: `ParentBased(TraceIdRatioBased(0.1))`, errors always; retention
  default 30 days; both in `subscriber.rs`.
