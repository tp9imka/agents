# AGENTS.md - <Project> (TypeScript / web)

<Project> is a TypeScript <5.x> pnpm workspace: `apps/web` (React <19> with
Vite, TanStack Router and Query), `apps/api` (Node <22>, Fastify), feature
packages under `packages/features/*`, shared packages under `packages/core/*`.
Strict TypeScript, Biome for lint and format, Vitest, Playwright. The seven
articles of `CONSTITUTION.md` apply; each names its gate below.

## Commands

- Setup: Node and pnpm versions from `package.json` `engines` and `packageManager` (use `corepack enable`); `pnpm install`.
- Check (the CI gate): `pnpm check` - `biome ci`, `tsc --noEmit -p tsconfig.json`, `depcruise --config .dependency-cruiser.cjs src packages apps`, codegen drift, `vitest run --coverage` (thresholds 100), Playwright smoke.
- Dev: `pnpm --filter web dev`; `pnpm --filter api dev`
- Test all: `pnpm test` (`vitest run` across the workspace)
- Test one package or file: `pnpm --filter @acme/orders test src/place-order.test.ts`; one test: add `-t "returns error when cart is empty"`
- Lint and format one package: `pnpm --filter @acme/orders exec biome check --write .`
- Type-check one package: `pnpm --filter @acme/orders exec tsc --noEmit`
- Codegen: `pnpm gen` (OpenAPI client, Prisma or Drizzle types); generated output is never edited.
- E2E: `pnpm --filter web e2e` (Playwright, needs the dev server; run only for UI changes).
- Iterate with the package's `vitest run <file>`; run `pnpm check` before declaring done.

## Architecture

- Feature-first packages: `packages/features/<name>` exposes `src/index.ts` (contracts, hooks, routes) and keeps `src/domain`, `src/application`, `src/adapters`, `src/ui` internal. Other packages import the entry point only; deep imports are forbidden. Gate: `.dependency-cruiser.cjs` rules `no-cross-feature-internals`, `no-circular`, `layers`.
- Dependency rule inside a feature: `domain` <= `application` <= `adapters`/`ui`. `domain` and `application` import no React, no fetch, no ORM. Gate: dependency-cruiser `layers` rule.
- DI: constructor injection for services; the composition root is `apps/api/src/app.ts` (Fastify plugins) and `apps/web/src/providers.tsx`. No module-level singletons that do I/O. Gate: dependency-cruiser forbids `adapters` imports outside the roots plus review.
- UI: TanStack Query owns server state; local UI state in a store hook per feature (Zustand slice) with immutable state and event-named actions; components render and dispatch. Gate: Biome `noRestrictedImports` for `fetch` inside `ui/`.
- Types are the spec: parse at the boundary with zod schemas in `adapters`, branded ids in `domain`, no `any`, no non-null assertions. Gate: `tsc` strict, Biome `noExplicitAny`, `noNonNullAssertion`.
- Layout and rules in full: `agent_docs/architecture.md`.

## Testing

- Test-first: the failing test comes first; a change whose tests pass with it stashed is not done. Gate: tdd-guard / Probity `PreToolUse` hook with the Vitest reporter (`.claude/settings.json`); review runs the stash check as backup.
- Coverage: `vitest.config.ts` sets `coverage.thresholds` to 100 for lines, branches, functions and statements per package; `coverage.exclude` lists only generated files, `*.d.ts` and the composition roots. Exclusions in code only: `/* v8 ignore next -- reason */`.
- Tests: Vitest with `describe`/`it` by behaviour, Testing Library for components (queries by role), `msw` for HTTP at the boundary, fakes for own ports in `packages/core/test-support`, fast-check properties for pure functions, Playwright for a few end-to-end flows.
- Mutation: `pnpm stryker run` on `packages/features/*` nightly; a score under 80% fails.
- Time and randomness are injected (`Clock`, `IdGenerator`); `Date.now()`, `new Date()` and `Math.random()` in `src/` outside `packages/core/clock` are forbidden. Gate: Biome `noRestrictedGlobals` plus a custom lint in `packages/core/lint`.
- Recipes: `agent_docs/testing.md`.

## Observability

- Every request, job and page view emits one canonical event through `packages/core/observability` (`CanonicalEvent`: `event.name`, `trace_id`, `outcome`, `error.type`, `duration_ms`, `user.id`, business fields). Emitted by the Fastify `onResponse` hook and the router's `onLoad` in `finally`; use cases add fields with `observe.add(...)`. Gate: `canonical-event.test.ts` per app asserts the event on success and failure.
- Logging: `pino` on the server and the `log` facade in the browser, both from `packages/core/observability`; child loggers per request carry `trace_id`. `console.*` is forbidden in `src/`. Gate: Biome `noConsole`.
- Levels: `debug` (dev), `info`, `error` with `error.type`; a `warn` must be actionable.
- Privacy: never log tokens, message bodies or free text; ids are fine. pino `redact` paths and the browser facade drop `password|token|secret|body|content|authorization`.
- Usage events: `packages/core/analytics/events.ts` (a discriminated union) is the catalogue; names `object_action` snake_case; `track(event)` takes the union only. Gate: `tsc` (the union) plus Biome `noRestrictedImports` for the vendor SDK outside `analytics/`.
- Performance: web vitals (LCP, INP, CLS) via `web-vitals` reported as events; User Timing marks around app-specific steps; OpenTelemetry JS on the server with `@fastify/otel` and the pg instrumentation; the four golden signals per route. Sampling: 10% traces, errors always; retention default 30 days (`observability/config.ts`).
- Setup and fields: `agent_docs/observability.md`.

## Boundaries

- Always: run the package's tests after each change and `pnpm check` before saying done; add a dependency-cruiser rule when you add an architectural rule; put new code in a `packages/features/*` or `packages/core/*` package, never in `apps/` except wiring, routes and providers.
- Ask first: adding a dependency (`pnpm add`); changing a feature's `src/index.ts` contract; adding an app or a package; bumping Node, TypeScript or React; editing `biome.json`, `.dependency-cruiser.cjs` or `.github/workflows/`.
- Never: commit secrets or `.env` (use `.env.example`); edit generated code (`*.generated.ts`, `prisma/client` - run `pnpm gen`); disable, delete or weaken a failing test (ask); use `console.*` (use the logger); deep-import another package's `src/` (use its entry point); use `any` or `!` (fix the type); run `pnpm test -- <filter>` with `--` (pnpm drops the filter and runs everything).

## Where to look

- `agent_docs/architecture.md` - package map, layer rules, the dependency-cruiser config, composition roots
- `agent_docs/testing.md` - Vitest patterns, Testing Library, msw, coverage thresholds, Stryker
- `agent_docs/observability.md` - canonical event hooks, pino setup, catalogue, web vitals, OTel, privacy
- `agent_docs/gates.md` - what `pnpm check` runs, CI, hooks
- Exemplars: `packages/features/orders/src/application/place-order.ts`, `packages/features/orders/src/adapters/orders-http-client.ts`, `packages/features/orders/src/application/place-order.test.ts`
- Legacy: none. When a legacy package appears, list it here and do not copy its patterns.

## Maintaining this file

- Add a line only after an observed failure, then re-run the task without and with the line and keep it only if the outcome changed. Every rule names its gate or its reason. Revisit after model releases. Stay under 150 lines.
