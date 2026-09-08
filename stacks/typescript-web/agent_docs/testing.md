# Testing - TypeScript / web

Rules in `CONSTITUTION.md` articles II and III.

## Workflow

1. Name the packages and types the change touches, in the task.
2. List the tests with behaviour names: `returns error when cart is empty`, `shows retry when the request fails`.
3. Per test: write it, run `pnpm --filter @acme/orders test src/application/place-order.test.ts -t "<name>"`, see it fail for the right reason, implement the minimum, run the package, refactor green.
4. Structural commits separate from behavioural ones.
5. Before done: `pnpm check`; every package touched reads 100 on all four metrics.

## Test types

| Level | Tool | Location |
|---|---|---|
| unit (domain, use cases, stores) | Vitest | next to the code, `*.test.ts` |
| property | fast-check | next to the code |
| adapter | Vitest with `msw` handlers; an in-memory or test database for repositories | `src/adapters/*.test.ts` |
| component | Testing Library (`getByRole`), `user-event` | `src/ui/*.test.tsx` |
| route | Fastify `inject` against `buildApp(fakeDeps())` | `apps/api/src/**/*.test.ts` |
| end to end | Playwright, few flows | `apps/web/e2e/` |

Fakes for own ports live in `packages/core/test-support`. `vi.mock` only for
third-party modules; never mock your own ports.

## Coverage gate

`vitest.config.ts` at the workspace root (inherited by every package):

```ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      all: true,
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['**/*.d.ts', '**/*.generated.ts', '**/*.test.{ts,tsx}', '**/index.ts', 'apps/*/src/{main.tsx,providers.tsx,app.ts,server.ts}'],
      thresholds: { lines: 100, branches: 100, functions: 100, statements: 100, perFile: true },
      reporter: ['text', 'lcov'],
    },
  },
});
```

Exclusions in code only: `/* v8 ignore next -- reason */`. Never lower a
threshold; never add a hand-written file to `exclude`.

## Mutation

`stryker.config.mjs` with `mutate: ['packages/features/*/src/**/!(*.test).ts']`,
`thresholds: { break: 80 }`; `pnpm stryker run` in `nightly.yml`.

## Rules

- `Clock` and `IdGenerator` from `packages/core/clock` are injected; `Date.now()`, `new Date()`, `Math.random()` in `src/` fail the custom lint.
- Failure path first: every rejected promise and every error branch has a test.
- No tests for constants, no assertion-free tests, no `it.skip` without a linked task.
- Testing Library queries by role and name; no `data-testid` unless there is no accessible handle.
- Do not pass `--` to `pnpm test`; the filter is dropped and the whole suite runs.
- Snapshot tests only for serialised outputs, updated with intent (`vitest -u` reviewed in the diff).
