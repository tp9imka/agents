# Gates - Python

Rules in `CONSTITUTION.md` article VI.

## `make check`

`Makefile`:

```make
check: fmt lint types arch migration-check test
fmt:             ; uv run ruff format --check src tests
lint:            ; uv run ruff check src tests
types:           ; uv run mypy --strict src
arch:            ; uv run lint-imports
migration-check: ; uv run alembic check
test:            ; uv run pytest
integration-test:; uv run pytest -m integration
```

`pytest` carries the coverage flags from `pyproject.toml`, so `make test`
fails below 100% branch coverage. CI runs exactly `make check`, then
`make integration-test` with Docker.

## Fast subset

- `uv run pytest tests/orders/application/test_place_order.py -x` for one file
- `-k <name>` for one test
- `uv run ruff format src/<project>/orders && uv run ruff check --fix src/<project>/orders`
- `uv run mypy src/<project>/orders`

## CI

`.github/workflows/check.yml`: `astral-sh/setup-uv`, `uv sync --all-groups`,
`make check`, then `make integration-test` with a Postgres service.
`nightly.yml`: mutmut with the gate script.

## Hooks

`prek` (or `pre-commit`) in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - { id: ruff-format, name: ruff format, entry: uv run ruff format, language: system, types: [python] }
      - { id: ruff, name: ruff check, entry: uv run ruff check --fix, language: system, types: [python] }
      - { id: mypy, name: mypy, entry: uv run mypy --strict src, language: system, pass_filenames: false, stages: [pre-push] }
      - { id: pytest, name: pytest, entry: uv run pytest -x -q, language: system, pass_filenames: false, stages: [pre-push] }
```

Agents: tdd-guard / Probity with the pytest reporter as a Claude Code
`PreToolUse` hook, and a `Stop` hook that runs `make check` and blocks until
it passes (`.claude/settings.json`).

## Fail closed

A missing tool, a migration diff or a coverage miss fails `make check`; nothing skips.
