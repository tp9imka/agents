# Gates - TypeScript / web

Rules in `CONSTITUTION.md` article VI.

## `pnpm check`

Root `package.json`:

```json
{
  "scripts": {
    "check": "pnpm biome ci . && pnpm typecheck && pnpm arch && pnpm gen:check && pnpm test:coverage && pnpm e2e:smoke",
    "typecheck": "tsc -b tsconfig.json",
    "arch": "depcruise --config .dependency-cruiser.cjs apps packages",
    "gen:check": "pnpm gen && git diff --exit-code -- '**/*.generated.ts'",
    "test": "vitest run",
    "test:coverage": "vitest run --coverage",
    "e2e:smoke": "playwright test --project=smoke"
  }
}
```

CI runs exactly `pnpm check`.

## Fast subset

- `pnpm --filter @acme/orders test src/application/place-order.test.ts` for one file
- `-t "<name>"` for one test
- `pnpm --filter @acme/orders exec biome check --write .` and `exec tsc --noEmit`
- `vitest --watch` while iterating on one package

## CI

`.github/workflows/check.yml`: `pnpm/action-setup`, `actions/setup-node` with
`cache: pnpm`, `pnpm install --frozen-lockfile`, `pnpm check`; Playwright
browsers cached. `nightly.yml`: Stryker and the full Playwright suite.

## Hooks

`lefthook.yml`:

```yaml
pre-commit:
  commands:
    biome: { glob: "*.{ts,tsx,json}", run: "pnpm biome check --write {staged_files} && git add {staged_files}" }
pre-push:
  commands:
    typecheck: { run: "pnpm typecheck" }
    test:      { run: "pnpm test" }
```

Agents: tdd-guard / Probity with the Vitest reporter as a Claude Code
`PreToolUse` hook, and a `Stop` hook that runs `pnpm check` and blocks until
it passes (`.claude/settings.json`).

## Fail closed

A missing browser, a codegen diff or a threshold miss fails `pnpm check`; nothing skips.
