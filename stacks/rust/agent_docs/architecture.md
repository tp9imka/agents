# Architecture - Rust

Hexagonal crates per feature; the compiler enforces the boundaries through
`Cargo.toml`, `cargo deny` and a crate-graph gate.

## Crate map

```
bins/api/src/main.rs                 composition root: config, subscriber, adapters, services, Axum router
crates/<feature>-domain/             newtypes, entities, invariants (validated constructors), error enums; no I/O crates
crates/<feature>-app/                Service trait + impl generic over ports; ports as traits (Repository, Clock, Notifier); src/testing.rs fakes
crates/<feature>-adapters/           axum routes and DTOs, sqlx repositories, HTTP clients; implements the ports
crates/infra-observability/          CanonicalEvent, the Axum layer, tracing subscriber, redaction, OTel export
crates/infra-analytics/              Event enum and Tracker
crates/infra-clock/, infra-db/       Clock impls, pool setup; no feature knowledge
arch/allowed.txt                     allowed crate edges for `just arch`
```

## Layer rules

- `-domain` depends on `thiserror`, `serde` at most; `deny.toml` bans `tokio`, `sqlx`, `axum`, `reqwest` for it.
- `-app` depends on `-domain` and `infra-observability` (for `#[instrument]` and the event builder); it declares ports as traits with `async fn` in traits (`Send` bounds spelled out) and never imports an adapter crate.
- `-adapters` depends on `-domain`, `-app` and infra crates; it never depends on another feature's adapters.
- Cross-feature: `orders-app` may depend on `users-app` (its public trait and constructor), never on `users-adapters` or `users-domain` internals.
- `bins/*` are the only crates allowed to depend on `-adapters` crates.

`just arch` runs `cargo modules dependencies --workspace --no-fns --no-types`
and diffs the crate edges against `arch/allowed.txt`; a new edge fails until
it is added there in the same change.

## Ports and services

```rust
// orders-app/src/ports.rs
#[async_trait]
pub trait OrdersRepository: Send + Sync {
    async fn save(&self, order: &Order) -> Result<(), RepoError>;
}

// orders-app/src/place_order.rs
pub struct PlaceOrder<R: OrdersRepository, C: Clock> { repo: R, clock: C, tracker: Tracker }
impl<R: OrdersRepository, C: Clock> PlaceOrder<R, C> {
    #[tracing::instrument(skip_all, fields(cart.items = cart.len()))]
    pub async fn execute(&self, cart: Cart) -> Result<OrderId, PlaceOrderError> { ... }
}
```

Generics in the core, `Arc<dyn Port>` only where a boundary needs erasure
(the Axum state). Wiring in `bins/api/src/main.rs`:

```rust
let repo = PgOrdersRepository::new(pool.clone());
let place_order = PlaceOrder::new(repo, SystemClock, obs.tracker());
let app = Router::new().merge(orders_adapters::routes(place_order)).layer(obs.layer());
```

## Types as specification

- Newtypes for every identifier (`OrderId(Uuid)`), validated constructors
  (`Email::parse`), enums instead of booleans, `NonZeroU32` where zero is invalid.
- Parse at the boundary (DTO => domain type in the adapter); the core never sees a `String` id.

## Errors

- One `thiserror` enum per layer; adapters map domain errors to HTTP status in
  `orders-adapters/src/http/error.rs`; nothing swallows an error with `let _ =`.
- `unwrap`/`expect` are denied by clippy outside tests and `main`.

## Size

- Modules under 500 lines of non-test code; above 800, split. No `mod.rs`; use `foo.rs` + `foo/`.
