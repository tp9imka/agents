# Testing - Rust

Rules in `CONSTITUTION.md` articles II and III.

## Workflow

1. Name the crates and types the change touches, in the task.
2. List the tests with behaviour names: `returns_error_when_cart_is_empty`, `persists_order_and_emits_event`.
3. Per test: write it, run `cargo nextest run -p orders-app <name>`, see it fail for the right reason, implement the minimum, run the crate, refactor green.
4. Structural commits separate from behavioural ones.
5. Before done: `just check`; coverage reads 100 lines and regions for the crates touched.

## Test types

| Level | Tool | Location |
|---|---|---|
| unit | `#[cfg(test)] mod tests`, `rstest` for cases | inside the module |
| property | `proptest` for parsers, invariants, serialisation round-trips | inside the module |
| doctest | every public item has a runnable example | doc comments; `cargo test --doc` in `check` |
| adapter | `sqlx::test` against Postgres (Docker), `wiremock` for HTTP clients | `crates/<feature>-adapters/tests/` |
| snapshot | `insta` for serialised responses; `cargo insta review` with intent | `tests/snapshots/` |

Fakes for own ports live in `<feature>-app/src/testing.rs` behind `#[cfg(any(test, feature = "testing"))]`.
No mocking crate for own traits; `mockall` only for third-party clients.

## Coverage gate

`justfile`:

```make
coverage:
    cargo llvm-cov nextest --workspace --all-features --branch \
        --ignore-filename-regex '^bins/|/tests/|_generated\.rs$' \
        --fail-under-lines 100 --fail-under-regions 100
```

Branch coverage needs the nightly `-C instrument-coverage` branch support;
regions are the stable proxy and are gated at 100. Exclusions in code only:

```rust
#[cfg_attr(coverage_nightly, coverage(off))] // reason: platform-specific fallback exercised in CI on linux only
fn ... {}
```

Never lower `--fail-under-*`; never widen the ignore regex for hand-written code.

## Mutation

`cargo mutants -p orders-domain -p orders-app --in-place` in `nightly.yml`;
`--minimum-test-timeout 20`; more than 20% missed mutants fails.

## Rules

- `Clock` and `Rng` are parameters; `SystemTime::now`, `Instant::now` in use cases and `rand::thread_rng` are in `clippy.toml` `disallowed-methods`.
- Failure path first: every error variant has a test that produces it.
- Compare whole values (`assert_eq!(actual, expected)`), not field by field.
- No tests for constants, no negative tests for removed code, no `#[ignore]` without a linked task.
- Snapshot updates are reviewed diffs, never `INSTA_UPDATE=always` in CI.
