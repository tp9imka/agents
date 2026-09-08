# Architecture - Python

Hexagonal per feature, enforced by import-linter; pydantic at the edges,
dataclasses in the core.

## Package map

```
src/<project>/app/main.py                  FastAPI app factory, lifespan, routers
src/<project>/app/container.py             composition root: build_adapters(settings), build_use_cases(adapters)
src/<project>/app/clock.py                 Clock protocol and SystemClock
src/<project>/<feature>/domain/            frozen dataclasses, NewType ids, invariants, errors; no I/O imports
src/<project>/<feature>/application/       use cases (callables), ports (typing.Protocol), DTOs
src/<project>/<feature>/adapters/          FastAPI router + pydantic schemas, SQLAlchemy repositories, clients
src/<project>/observability/               CanonicalEvent, middleware, logging (structlog), otel, redact
src/<project>/analytics/                   event dataclasses, track()
src/<project>/db/                          engine, session factory, alembic env - no feature knowledge
tests/                                     mirrors src/; tests/support/fakes.py
.importlinter                              the layer gate
```

## Layer rules

`.importlinter`:

```ini
[importlinter]
root_package = <project>

[importlinter:contract:layers]
name = feature layers
type = layers
containers = <project>.orders, <project>.users
layers =
    adapters
    application
    domain

[importlinter:contract:domain-pure]
name = domain imports no I/O
type = forbidden
source_modules = <project>.orders.domain, <project>.users.domain
forbidden_modules = fastapi, sqlalchemy, httpx, pydantic, <project>.db

[importlinter:contract:features]
name = features are independent except through application
type = independence
modules = <project>.orders, <project>.users
ignore_imports =
    <project>.orders.application -> <project>.users.application

[importlinter:contract:adapters-from-root]
name = only app and adapters see adapters
type = forbidden
source_modules = <project>.*.application, <project>.*.domain
forbidden_modules = <project>.*.adapters
```

Add a contract in the same change as any new architectural rule.

## Composition root

```python
# app/container.py
def build(settings: Settings) -> Container:
    engine = make_engine(settings.db)
    orders_repo = SqlAlchemyOrdersRepository(engine)
    return Container(place_order=PlaceOrder(orders_repo, SystemClock(), tracker))
```

Routers receive use cases through `Depends(get_container)` at the edge only.
No module-level engines, sessions or clients; tests build a container with fakes.

## Types as specification

- pydantic models only in `adapters` (request/response parsing); the core uses
  `@dataclass(frozen=True, slots=True)` and `NewType("OrderId", str)` ids.
- `mypy --strict`; `Protocol` for ports; enums instead of booleans for modes.
- Parse at the boundary, never re-validate inside.

## Async rules

- `async def` routes never call blocking code (no `time.sleep`, no sync DB
  session, no sync `requests`); blocking work goes in a sync route (threadpool)
  or `anyio.to_thread.run_sync`. ruff `ASYNC` rules enforce the common cases.
- One session per request from `db.session()`; never a global session.

## Size

- A module above 500 lines or a use case above 100 lines is split.
- Shared code moves to a top-level package when a second feature needs it.
