# AGENTS.md - <Project> (Go)

<Project> is a Go <1.2x> service: HTTP (chi) and gRPC transports over one
use-case layer, Postgres through pgx and sqlc, `log/slog` and OpenTelemetry.
Layout: `cmd/<binary>/`, `internal/<feature>/{domain,app,ports,adapters}`,
`internal/app/` (composition root), `pkg/` for transport-agnostic infrastructure.
The seven articles of `CONSTITUTION.md` apply; each names its gate below.

## Commands

- Setup: Go from `go.mod`; `make bin-deps` installs golangci-lint, go-arch-lint, go-test-coverage, sqlc, gremlins into `bin/`.
- Check (the CI gate): `make check` - `gofmt -l`, `golangci-lint run`, `go-arch-lint check`, sqlc drift check, `go test -race -covermode=atomic -coverprofile=coverage.out ./...`, `go-test-coverage --config .testcoverage.yml` (100% per file).
- Build: `go build ./...`; run: `go run ./cmd/api`
- Test all: `go test -race ./...`
- Test one package or test: `go test -race ./internal/orders/... -run TestPlaceOrder_ReturnsErrorWhenCartEmpty`
- Lint one package: `golangci-lint run ./internal/orders/...`
- Integration tests (Postgres in Docker): `make integration-test` (uses testcontainers; needs Docker). `go test ./integration/...` on the host fails on hostnames by design.
- Codegen: `make gen` (sqlc, mocks for third-party ports); generated files are never edited.
- Iterate with the package's `go test`; run `make check` before declaring done.

## Architecture

- Feature-first packages: `internal/<feature>/domain` (entities, errors; imports nothing from this module), `app` (use cases, `ports.go` with the interfaces the use cases need), `adapters` (`http/`, `grpc/`, `postgres/`). Features import other features only through their `app` interfaces. Gate: `.go-arch-lint.yml` in `make check`.
- Dependency rule: `domain` <= `app` <= `adapters`; `pkg/` never imports `internal/`; wiring happens once in `internal/app/app.go`. Gate: go-arch-lint plus `internal/` visibility.
- DI: constructors named `New`, taking interfaces, returning concrete types; wired by hand in `internal/app/app.go`. No package-level globals, no `init()` wiring. Gate: golangci-lint `gochecknoglobals`, `gochecknoinits`.
- Handler contract: decode into a transport-local DTO, validate, call the use case with domain types, map errors to status codes in the adapter. Never pass a request DTO into a use case. Gate: review plus `depguard` rules.
- Errors are values: wrap with `fmt.Errorf("op: %w", err)`, sentinel errors in `domain`, `errors.Is/As` at the boundary; no `panic` outside `main`. Gate: golangci-lint `errorlint`, `wrapcheck`.
- Layout and rules in full: `agent_docs/architecture.md`.

## Testing

- Test-first: the failing test comes first; a change whose tests pass with it stashed is not done. Gate: tdd-guard / Probity `PreToolUse` hook with the Go reporter (`.claude/settings.json`); review runs the stash check as backup.
- Coverage: `.testcoverage.yml` sets `threshold: { file: 100, package: 100, total: 100 }` on branch-equivalent statement coverage; generated code and `cmd/` are excluded there. No line pragma exists in Go: restructure until the branch is reachable, or move the untestable I/O behind a port.
- Tests: table-driven with `t.Run`, `testify/require` for assertions, fakes for own ports in `internal/<feature>/apptest`, mocks only for third-party clients (`make gen`). Integration tests with testcontainers under `integration/`.
- Mutation: `gremlins unleash ./internal/...` nightly; efficacy under 80% fails.
- Time and randomness are injected (`clock.Clock`, `io.Reader`); `time.Now()` outside `internal/app` and `pkg/clock` is forbidden. Gate: `forbidigo`.
- Recipes: `agent_docs/testing.md`.

## Observability

- Every request, gRPC call, job and message emits one canonical event through `pkg/observability` (`CanonicalEvent`: `event.name`, `trace_id`, `outcome`, `error.type`, `duration_ms`, `user.id`, business fields) from the middleware in `pkg/observability/middleware.go`, in a `defer`; handlers add fields with `observability.Add(ctx, key, value)`. Gate: `middleware_test.go` per transport asserts the event on success and failure.
- Logging: `log/slog` with the JSON handler from `pkg/observability/logger.go`; loggers come from the context (`observability.Logger(ctx)`). `fmt.Print*`, `log.Print*` and `println` are forbidden. Gate: `forbidigo`.
- Levels: `Debug` (dev), `Info` (operators), `Error` with `error.type`; a `Warn` must be actionable. Libraries return errors; they do not log.
- Privacy: never log tokens, passwords, message bodies or free text; ids are fine. `pkg/observability/redact.go` drops keys matching `password|token|secret|body|content` in the handler.
- Usage events: `pkg/analytics/events.go` typed constructors are the catalogue; names `object_action` snake_case; `analytics.Track(ctx, ev)` takes the typed value only. Gate: `depguard` forbids other importers of the transport client.
- Performance: OpenTelemetry Go SDK (`pkg/observability/otel.go`) with `otelhttp`, `otelgrpc`, `otelpgx`; the four golden signals per endpoint from the middleware; `pprof` on the admin port. Sampling: parent-based 10%, errors 100%; retention default 30 days (`otel.go`).
- Setup and fields: `agent_docs/observability.md`.

## Boundaries

- Always: run the package's tests after each change and `make check` before saying done; add a `.go-arch-lint.yml` rule when you add an architectural rule; put new code in `internal/<feature>/` or `pkg/`, never in `cmd/` except flags and startup.
- Ask first: adding a module to `go.mod` (`go get`); changing a `ports.go` interface used by another feature; adding a transport; editing `.golangci.yml`, `.go-arch-lint.yml` or `.github/workflows/`; bumping the Go version.
- Never: commit secrets or `.env` (use `.env.example` and `envconfig`); edit generated code (`*.sql.go`, mocks - run `make gen`); disable, delete or weaken a failing test (ask); use `fmt.Print*` or `log.Print*` (use `observability.Logger(ctx)`); import another feature's `adapters` or `domain` (use its `app` interface); use `time.Now()` in use cases (inject `clock.Clock`); suppress a lint finding with a bare `//nolint` (add the reason after `//`).

## Where to look

- `agent_docs/architecture.md` - package map, layer rules, the go-arch-lint config, wiring in `internal/app`
- `agent_docs/testing.md` - table tests, fakes, testcontainers, `.testcoverage.yml`, gremlins
- `agent_docs/observability.md` - canonical event middleware, slog setup, catalogue, OTel, privacy
- `agent_docs/gates.md` - what `make check` runs, CI, hooks
- Exemplars: `internal/orders/app/place_order.go`, `internal/orders/adapters/postgres/orders_repo.go`, `internal/orders/app/place_order_test.go`
- Legacy: none. When a legacy package appears, list it here and do not copy its patterns.

## Maintaining this file

- Add a line only after an observed failure, then re-run the task without and with the line and keep it only if the outcome changed. Every rule names its gate or its reason. Revisit after model releases. Stay under 150 lines.
