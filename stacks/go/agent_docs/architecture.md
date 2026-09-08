# Architecture - Go

The official module layout (`cmd/`, `internal/`, a small `pkg/`) with a
feature-first split inside `internal/`. Add directories when a need appears,
not for symmetry.

## Package map

```
cmd/api/main.go                       flags, config, calls internal/app.Run
cmd/worker/main.go
internal/app/app.go                   composition root: builds adapters, wires use cases, starts transports
internal/<feature>/
  domain/                             entities, value types, sentinel errors; imports nothing from this module
  app/                                use cases (one type per use case), ports.go (interfaces the use cases need), apptest/ fakes
  adapters/http/                      chi handlers, request/response DTOs, error mapping
  adapters/grpc/                      grpc servers, proto mapping
  adapters/postgres/                  sqlc queries, repository types implementing the ports
pkg/observability/                    CanonicalEvent, middleware, logger, otel, redact
pkg/analytics/                        typed event constructors, Track
pkg/clock/, pkg/postgres/, pkg/httpserver/   transport-agnostic infrastructure; never imports internal/
integration/                          testcontainers suites
.go-arch-lint.yml                     the layer gate
```

## Layer rules

`.go-arch-lint.yml`:

```yaml
version: 3
workdir: .
allow: { depOnAnyVendor: false }
components:
  domain:   { in: internal/*/domain/** }
  app:      { in: internal/*/app/** }
  adapters: { in: internal/*/adapters/** }
  root:     { in: internal/app/** }
  pkg:      { in: pkg/** }
  cmd:      { in: cmd/** }
vendors:
  chi:  { in: github.com/go-chi/chi/** }
  pgx:  { in: github.com/jackc/pgx/** }
  otel: { in: go.opentelemetry.io/** }
deps:
  domain:   { anyVendorDeps: false }
  app:      { mayDependOn: [domain, pkg] }
  adapters: { mayDependOn: [domain, app, pkg], canUse: [chi, pgx, otel] }
  root:     { mayDependOn: [domain, app, adapters, pkg] }
  cmd:      { mayDependOn: [root, pkg] }
  pkg:      { canUse: [otel, pgx, chi] }
```

Cross-feature calls: `internal/orders/app` may import `internal/users/app`
(an interface and a constructor), never `internal/users/adapters` or `domain`
internals. Add a `depguard` rule in `.golangci.yml` when a feature must stay isolated.

## Wiring

```go
// internal/app/app.go
func Run(ctx context.Context, cfg Config) error {
    obs := observability.New(cfg.Observability)
    db := postgres.Connect(ctx, cfg.DB)
    orders := ordersapp.New(orderspg.NewRepo(db), clock.System{}, obs.Tracker())
    srv := httpserver.New(cfg.HTTP, obs.Middleware(), ordershttp.Routes(orders))
    return srv.Run(ctx)
}
```

Constructors are `New`, take interfaces, return concrete types. No globals,
no `init()` (golangci-lint `gochecknoglobals`, `gochecknoinits`). Fx is the
documented option once wiring exceeds roughly 200 lines.

## Handler contract

1. Authenticate from context; a failure here is 401/403, not 500.
2. Decode into `request.PlaceOrder` (transport-local DTO); validate with `validator`.
3. Map to domain types; call `usecase.Execute(ctx, cmd)`.
4. Map domain errors with `errors.Is` to status codes in one place (`adapters/http/errors.go`).
5. Encode `response.Order`. Domain types never cross the transport boundary.

## Rules that keep it simple

- Functions over types; no interface with one implementation unless it is a port.
- Accept interfaces, return structs. Keep interfaces small and defined where used.
- Context first argument; never stored in a struct.
- A package above roughly 800 lines of non-test code is split by responsibility.
