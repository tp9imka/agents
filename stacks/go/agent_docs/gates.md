# Gates - Go

Rules in `CONSTITUTION.md` article VI.

## `make check`

`Makefile`, in order:

```make
check: fmt-check lint arch gen-check test coverage
fmt-check:  ; test -z "$$(gofmt -l .)"
lint:       ; bin/golangci-lint run
arch:       ; bin/go-arch-lint check
gen-check:  ; $(MAKE) gen && git diff --exit-code -- '*.sql.go' '*_mock.go'
test:       ; go test -race -covermode=atomic -coverprofile=coverage.out ./...
coverage:   ; bin/go-test-coverage --config .testcoverage.yml
integration-test: ; go test -race -tags integration ./integration/...
```

CI runs exactly `make check` plus `make integration-test` with Docker.

## Fast subset

- `go test -race ./internal/orders/...` for one package
- `-run TestPlaceOrder_ReturnsErrorWhenCartEmpty` for one test
- `bin/golangci-lint run ./internal/orders/...` for one package
- `gofmt -w internal/orders`

## CI

`.github/workflows/check.yml`: `actions/setup-go` with `go.mod` version,
`make bin-deps`, `make check`, then `make integration-test` (Docker service).
`nightly.yml`: gremlins mutation run.

## Hooks

`lefthook.yml`:

```yaml
pre-commit:
  commands:
    fmt:  { glob: "*.go", run: "gofmt -w {staged_files} && git add {staged_files}" }
    lint: { glob: "*.go", run: "bin/golangci-lint run --new-from-rev=HEAD" }
pre-push:
  commands:
    test: { run: "go test -race ./..." }
```

Agents: tdd-guard / Probity with the Go reporter as a Claude Code
`PreToolUse` hook, and a `Stop` hook that runs `make check` and blocks until
it passes (`.claude/settings.json`).

## Fail closed

A missing `bin/` tool fails `make check` with the install hint; nothing skips.
