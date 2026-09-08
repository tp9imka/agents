# Gates - Rust

Rules in `CONSTITUTION.md` article VI.

## `just check`

`justfile`:

```make
check: fmt lint deny arch gen-check test doc coverage
fmt:        ; cargo fmt --all --check
lint:       ; cargo clippy --workspace --all-targets --all-features -- -D warnings
deny:       ; cargo deny check
arch:       ; cargo modules dependencies --workspace --no-fns --no-types --no-traits | scripts/edges.sh | diff - arch/allowed.txt
gen-check:  ; cargo sqlx prepare --check --workspace
test:       ; cargo nextest run --workspace --all-features
doc:        ; cargo test --doc --workspace
coverage:   ; cargo llvm-cov nextest --workspace --all-features --fail-under-lines 100 --fail-under-regions 100
```

CI runs exactly `just check`, then `just integration` with a Postgres service.

## Fast subset

- `cargo nextest run -p orders-app` for one crate; add a name filter for one test
- `cargo clippy -p orders-app --all-targets -- -D warnings`
- `cargo fmt -p orders-app`
- `cargo check` for a fast type check while iterating

## CI

`.github/workflows/check.yml`: `dtolnay/rust-toolchain` with the pinned
toolchain, `Swatinem/rust-cache`, `just check`, `just integration`.
`nightly.yml`: `cargo mutants` and the nightly-only branch-coverage report.

## Hooks

`lefthook.yml`:

```yaml
pre-commit:
  commands:
    fmt:  { glob: "*.rs", run: "cargo fmt --all" }
    lint: { glob: "*.rs", run: "cargo clippy --all-targets -- -D warnings" }
pre-push:
  commands:
    test: { run: "cargo nextest run --workspace" }
```

Agents: tdd-guard / Probity with the cargo reporter as a Claude Code
`PreToolUse` hook, and a `Stop` hook that runs `just check` and blocks until
it passes (`.claude/settings.json`).

## Fail closed

A missing tool fails `just check` with the `cargo install` hint; nothing skips.
