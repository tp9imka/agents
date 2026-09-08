# AGENTS.md - <Project> (Rust)

<Project> is a Rust <1.8x> workspace pinned in `rust-toolchain.toml`: Axum
HTTP, sqlx with Postgres, tokio, `tracing` and OpenTelemetry. Crates:
`crates/<feature>-domain`, `crates/<feature>-app`, `crates/<feature>-adapters`,
`crates/infra-*`, `bins/api`. The seven articles of `CONSTITUTION.md` apply;
each names its gate below.

## Commands

- Setup: `rustup show` (installs the pinned toolchain); `cargo install cargo-nextest cargo-llvm-cov cargo-mutants cargo-modules sqlx-cli just`.
- Check (the CI gate): `just check` - `cargo fmt --check`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo deny check`, crate-graph gate, `sqlx` offline drift check, `cargo llvm-cov nextest --all-features --fail-under-lines 100 --fail-under-regions 100`, doc tests.
- Build: `cargo build`; run: `cargo run -p api`
- Test all: `cargo nextest run --all-features` (plus `cargo test --doc`)
- Test one crate or test: `cargo nextest run -p orders-app place_order::returns_error_when_cart_empty`
- Lint one crate: `cargo clippy -p orders-app --all-targets -- -D warnings`
- Coverage report: `cargo llvm-cov nextest --html` => `target/llvm-cov/html/index.html`
- Integration tests (Postgres in Docker): `just integration` (sqlx test with a database URL); needs Docker.
- Iterate with `cargo nextest run -p <crate>`; run `just check` before declaring done.

## Architecture

- Feature-first crates: `<feature>-domain` (types, invariants, errors; depends on no I/O crate), `<feature>-app` (services as traits and their implementations, ports as traits), `<feature>-adapters` (Axum routes, sqlx repositories, clients). Features depend on other features through their `-app` crate's public traits only. Gate: `Cargo.toml` dependencies plus `just arch` (`cargo-modules` graph diff against `arch/allowed.txt`).
- Dependency rule: `domain` <= `app` <= `adapters`; `bins/api` wires them. Nothing in `-domain` depends on tokio, sqlx or axum. Gate: `cargo deny` bans those crates for `-domain` targets in `deny.toml`.
- DI: generics with trait bounds at construction, `Arc<dyn Port>` only at the boundary; wiring in `bins/api/src/main.rs`. No global state, no `lazy_static` for services. Gate: clippy plus review.
- Errors: `thiserror` enums per layer; `?` everywhere; `unwrap`/`expect` only in tests and `main`. Gate: clippy `unwrap_used`, `expect_used` deny in `Cargo.toml` lints.
- Modules under 500 lines of non-test code; above 800, add a module. `mod.rs` files are not used. Gate: review; `just check` warns via `tokei`.
- Layout and rules in full: `agent_docs/architecture.md`.

## Testing

- Test-first: the failing test comes first; a change whose tests pass with it stashed is not done. Gate: tdd-guard / Probity `PreToolUse` hook with the cargo reporter (`.claude/settings.json`); review runs the stash check as backup.
- Coverage: `cargo llvm-cov` with `--fail-under-lines 100 --fail-under-regions 100`; `bins/` and generated code excluded in `.cargo/llvm-cov.toml`. Exclusions in code only: `#[cfg_attr(coverage_nightly, coverage(off))]` with a reason on the line above.
- Tests: unit tests in `#[cfg(test)]` modules, integration tests in `tests/`, doctests on every public item (they run in `check`), `proptest` for pure functions, `insta` snapshots for serialised outputs (goldens updated only with intent), fakes for own ports in `<feature>-app/src/testing.rs`.
- Mutation: `cargo mutants --in-place -p '<feature>-domain' -p '<feature>-app'` nightly; missed mutants above 20% fail.
- Time and randomness are injected (`Clock` trait, `rand::Rng` parameter); `SystemTime::now()` and `Utc::now()` outside `infra-clock` and `main` are forbidden. Gate: clippy `disallowed_methods` in `clippy.toml`.
- Recipes: `agent_docs/testing.md`.

## Observability

- Every request, job and message emits one canonical event through `infra-observability` (`CanonicalEvent`: `event.name`, `trace_id`, `outcome`, `error.type`, `duration_ms`, `user.id`, business fields) from the Axum layer in `infra-observability/src/layer.rs` in a `Drop` guard; use cases are `#[tracing::instrument(skip_all, fields(...))]` so their spans carry the trace id. Gate: `layer_test.rs` asserts the event on success and failure.
- Logging: `tracing` macros only, with the JSON subscriber from `infra-observability/src/subscriber.rs`. `println!`, `eprintln!`, `dbg!` and the `log` crate are forbidden in `src/`. Gate: clippy `print_stdout`, `print_stderr`, `dbg_macro` deny; `cargo deny` bans `log`.
- Levels: `debug` (dev), `info`, `error` with `error.type`; a `warn` must be actionable. Library crates emit events; they do not decide sinks.
- Privacy: never log tokens, message bodies or free text; ids are fine. Fields named `password|token|secret|body|content` are redacted by the subscriber layer in `subscriber.rs`.
- Usage events: `infra-analytics/src/events.rs` enum is the catalogue; names `object_action` snake_case; `Tracker::track(Event)` takes the enum only. Gate: the enum is the only public constructor.
- Performance: `tracing-opentelemetry` exports spans OTLP; `axum` middleware records latency, traffic, errors and in-flight per route (`metrics` crate); `tokio-console` in dev; `cargo flamegraph` for CPU. Sampling: parent-based 10%, errors always; retention default 30 days (`subscriber.rs`).
- Setup and fields: `agent_docs/observability.md`.

## Boundaries

- Always: run the crate's tests after each change and `just check` before saying done; update `arch/allowed.txt` when you add an allowed crate edge; put new code in a `crates/<feature>-*` crate, never in `bins/` except wiring.
- Ask first: adding a dependency (`cargo add`) or changing `deny.toml`; changing a public trait in a `-app` crate used by another feature; bumping the toolchain in `rust-toolchain.toml`; editing `justfile`, `clippy.toml` or `.github/workflows/`.
- Never: commit secrets or `.env` (use `.env.example`); edit `sqlx-data.json` or generated code by hand (run `just gen`); disable, delete or weaken a failing test (ask); use `println!`/`dbg!` (use `tracing`); add `#[allow(...)]` to pass CI (fix the lint, or ask with the reason); write `unsafe` (ask; if approved, a `// SAFETY:` comment is required); depend on another feature's `-adapters` or `-domain` internals (use its `-app` traits).

## Where to look

- `agent_docs/architecture.md` - crate map, trait-based ports and services, wiring, the graph gate
- `agent_docs/testing.md` - nextest, doctests, proptest, insta, llvm-cov config, cargo-mutants
- `agent_docs/observability.md` - canonical event layer, tracing subscriber, catalogue, OTel, privacy
- `agent_docs/gates.md` - what `just check` runs, CI, hooks
- Exemplars: `crates/orders-app/src/place_order.rs`, `crates/orders-adapters/src/postgres/orders_repo.rs`, `crates/orders-app/src/place_order.rs` (tests module)
- Legacy: none. When a legacy crate appears, list it here and do not copy its patterns.

## Maintaining this file

- Add a line only after an observed failure, then re-run the task without and with the line and keep it only if the outcome changed. Every rule names its gate or its reason. Revisit after model releases. Stay under 150 lines.
