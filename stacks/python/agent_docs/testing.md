# Testing - Python

Rules in `CONSTITUTION.md` articles II and III.

## Workflow

1. Name the packages and types the change touches, in the task.
2. List the tests with behaviour names: `test_returns_error_when_cart_is_empty`, `test_persists_order_and_emits_event`.
3. Per test: write it, run `uv run pytest tests/orders/application/test_place_order.py -k <name> -x`, see it fail for the right reason, implement the minimum, run the file, refactor green.
4. Structural commits separate from behavioural ones.
5. Before done: `make check`; `fail_under = 100` with branches for the whole package.

## Test types

| Level | Tool | Location |
|---|---|---|
| unit (domain, use cases) | pytest, `parametrize` | `tests/<feature>/domain`, `tests/<feature>/application` |
| property | Hypothesis with the examples database committed | same |
| adapter | `httpx.AsyncClient(transport=ASGITransport(app))` for routes; testcontainers Postgres for repositories | `tests/<feature>/adapters` |
| doctest | pure functions carry examples; `pytest --doctest-modules src` runs in `check` | in docstrings |
| integration | `-m integration`, Docker | `tests/integration` |

Fakes for own ports live in `tests/support/fakes.py` (small classes
implementing the `Protocol`). `unittest.mock` only for third-party clients,
always with `autospec=True`.

## Coverage gate

`pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = "--cov=<project> --cov-branch --cov-report=term-missing:skip-covered --cov-report=xml --doctest-modules --strict-markers -p no:cacheprovider"
testpaths = ["tests", "src"]

[tool.coverage.run]
branch = true
source = ["src/<project>"]
omit = ["src/<project>/db/migrations/*", "src/<project>/app/main.py", "*/generated/*"]

[tool.coverage.report]
fail_under = 100
show_missing = true
exclude_also = ["if TYPE_CHECKING:", "\\.\\.\\.$"]   # Protocol bodies and typing-only blocks
```

Exclusions in code only: `# pragma: no cover  # reason`. Never lower
`fail_under`; never add hand-written files to `omit`.

## Mutation

`uv run mutmut run --paths-to-mutate src/<project> --tests-dir tests` in
`nightly.yml`; the job fails when survivors exceed 20% (`mutmut results` parsed
in `scripts/mutation_gate.py`).

## Rules

- `Clock` and a `random.Random` instance are injected; `datetime.now()`,
  `time.time()` and `random.*` in `src/` fail the `banned-api` lint outside `app/clock.py`.
- `time-machine` for time-dependent tests; never sleep in tests.
- Failure path first: every raised exception and every error result has a test.
- No tests for constants, no assertion-free tests, no `skip` without a linked task.
- Structured log assertions through `structlog.testing.capture_logs()`, never string matching on output.
