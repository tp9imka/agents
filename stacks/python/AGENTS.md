# AGENTS.md - <Project> (Python)

<Project> is a Python <3.1x> service: FastAPI, SQLAlchemy 2 with Postgres,
structlog, OpenTelemetry, managed with `uv`. Layout: `src/<project>/<feature>/`
with `domain`, `application`, `adapters` per feature, `src/<project>/app/`
as the composition root, `tests/` mirroring `src/`. The seven articles of
`CONSTITUTION.md` apply; each names its gate below.

## Commands

- Setup: `uv sync --all-groups` (Python version from `.python-version`; never the system interpreter). `uv run` for everything.
- Check (the CI gate): `make check` - `ruff format --check`, `ruff check`, `mypy --strict`, `lint-imports`, migration drift check, `pytest --cov --cov-branch --cov-fail-under=100 -p no:cacheprovider`.
- Run: `uv run uvicorn <project>.app.main:app --reload`
- Test all: `uv run pytest`
- Test one file or test: `uv run pytest tests/orders/application/test_place_order.py -k "returns_error_when_cart_is_empty" -x`
- Lint and format one package: `uv run ruff format src/<project>/orders && uv run ruff check --fix src/<project>/orders`
- Type-check: `uv run mypy src`
- Migrations: `uv run alembic revision --autogenerate -m "<what>"` then `make migration-check`; never edit an applied migration.
- Integration tests (Postgres in Docker): `make integration-test` (testcontainers); the unit suite needs no services.
- Iterate with `pytest <file> -x`; run `make check` before declaring done.

## Architecture

- Feature-first packages: `src/<project>/<feature>/domain` (dataclasses, value objects, errors; imports nothing with I/O), `application` (use cases, ports as `Protocol`s, DTOs), `adapters` (FastAPI routers, SQLAlchemy repositories, clients). Features import other features through their `application` package only. Gate: `.importlinter` layers and independence contracts in `make check`.
- Dependency rule: `domain` <= `application` <= `adapters`; `app/` wires them. Gate: import-linter.
- DI: constructor injection; the composition root is `src/<project>/app/container.py` (plain functions building adapters and use cases) exposed to FastAPI through `Depends` at the router edge only. No module-level clients or sessions. Gate: import-linter forbids `adapters` imports outside `app/` and `adapters/` tests; ruff `PLW0603` (no globals).
- Types are the spec: pydantic models parse at the boundary in `adapters`; the core uses frozen dataclasses and `NewType` ids; `mypy --strict` passes with no `Any` and no `type: ignore` without a reason. Gate: mypy.
- Async routes never block (no `time.sleep`, no sync DB calls in `async def`); sync work goes to sync routes or a thread. Gate: ruff `ASYNC` rules.
- Layout and rules in full: `agent_docs/architecture.md`.

## Testing

- Test-first: the failing test comes first; a change whose tests pass with it stashed is not done. Gate: tdd-guard / Probity `PreToolUse` hook with the pytest reporter (`.claude/settings.json`); review runs the stash check as backup.
- Coverage: `pyproject.toml` `[tool.coverage.report] fail_under = 100` with `branch = true`; `omit` lists only migrations, `app/main.py` and generated code. Exclusions in code only: `# pragma: no cover  # reason`.
- Tests: pytest with `parametrize` for cases, `Hypothesis` for pure functions, fakes for own ports in `tests/support/fakes.py`, `httpx.AsyncClient` with `ASGITransport` for routes, testcontainers for repositories, `time-machine` for time. No `unittest.mock` on own ports.
- Mutation: `uv run mutmut run --paths-to-mutate src/<project>` nightly; survivors above 20% fail.
- Time and randomness are injected (`Clock` protocol, `random.Random` instance); `datetime.now()` and `random.random()` in `src/` outside `<project>/app/clock.py` are forbidden. Gate: ruff `DTZ` rules plus a `banned-api` entry in `pyproject.toml`.
- Recipes: `agent_docs/testing.md`.

## Observability

- Every request, job and message emits one canonical event through `src/<project>/observability` (`CanonicalEvent`: `event.name`, `trace_id`, `outcome`, `error.type`, `duration_ms`, `user.id`, business fields) from the ASGI middleware in `observability/middleware.py` in a `finally`; use cases add fields with `observe.add(...)`. Gate: `tests/observability/test_canonical_event.py` asserts the event on success and failure.
- Logging: structlog configured in `observability/logging.py` (JSON renderer, contextvars bound per request). `print` and the stdlib `logging` module calls outside the configuration are forbidden. Gate: ruff `T201`, `T203` and a `banned-api` entry for `logging.getLogger` outside `observability/`.
- Levels: `debug` (dev), `info`, `error` with `error.type`; a `warning` must be actionable.
- Privacy: never log tokens, message bodies or free text; ids are fine. The structlog processor `redact_sensitive` in `observability/logging.py` drops `password|token|secret|body|content|authorization`.
- Usage events: `src/<project>/analytics/events.py` (frozen dataclasses with a `name` class attribute) is the catalogue; names `object_action` snake_case; `track(event)` takes those types only. Gate: mypy plus a `banned-api` entry for the vendor SDK outside `analytics/`.
- Performance: OpenTelemetry Python with `FastAPIInstrumentor`, `SQLAlchemyInstrumentor` and `HTTPXClientInstrumentor`; the four golden signals per route from the middleware; `py-spy` for profiling. Sampling: parent-based 10%, errors always; retention default 30 days (`observability/config.py`).
- Setup and fields: `agent_docs/observability.md`.

## Boundaries

- Always: run the file's tests after each change and `make check` before saying done; add an import-linter contract when you add an architectural rule; put new code in `src/<project>/<feature>/` or `src/<project>/<shared>/`, never in `app/` except wiring and routes.
- Ask first: adding a dependency (`uv add`); changing an `application` port used by another feature; adding a migration that alters a column in place; bumping the Python version; editing `pyproject.toml` tool sections, `.importlinter` or `.github/workflows/`.
- Never: commit secrets or `.env` (use `.env.example` and `pydantic-settings`); edit an applied migration (add a new one); disable, delete or weaken a failing test (ask); use `print` or `logging.getLogger` (use `structlog.get_logger()` from `observability`); import another feature's `adapters` or `domain` internals (use its `application` package); block the event loop in an `async def` (sync route or a thread); add `# type: ignore` or `# noqa` without a reason.

## Where to look

- `agent_docs/architecture.md` - package map, layer contracts, the container, async rules
- `agent_docs/testing.md` - pytest patterns, fakes, Hypothesis, coverage config, mutmut
- `agent_docs/observability.md` - canonical event middleware, structlog setup, catalogue, OTel, privacy
- `agent_docs/gates.md` - what `make check` runs, CI, hooks
- Exemplars: `src/<project>/orders/application/place_order.py`, `src/<project>/orders/adapters/sqlalchemy_repo.py`, `tests/orders/application/test_place_order.py`
- Legacy: none. When a legacy package appears, list it here and do not copy its patterns.

## Maintaining this file

- Add a line only after an observed failure, then re-run the task without and with the line and keep it only if the outcome changed. Every rule names its gate or its reason. Revisit after model releases. Stay under 150 lines.
