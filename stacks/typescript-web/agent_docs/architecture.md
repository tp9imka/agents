# Architecture - TypeScript / web

Feature-first packages in a pnpm workspace with the dependency rule enforced
by dependency-cruiser.

## Package map

```
apps/web/src/main.tsx, providers.tsx, router.tsx     composition root for the browser
apps/api/src/app.ts, server.ts                        composition root for the server (Fastify plugins)
packages/features/<name>/src/index.ts                 the public entry: hooks, route definitions, contracts, events
packages/features/<name>/src/domain/                  types, branded ids, invariants, pure functions - no React, no fetch
packages/features/<name>/src/application/             use cases, ports (interfaces), commands and queries
packages/features/<name>/src/adapters/                HTTP clients (zod-parsed), repositories, vendor SDK wrappers
packages/features/<name>/src/ui/                      components, the feature store hook, TanStack Query hooks
packages/core/observability/                          CanonicalEvent, logger (pino + browser facade), otel, redact
packages/core/analytics/                              event union, track
packages/core/clock/, core/http/, core/design-system/ shared infrastructure, no feature knowledge
packages/core/test-support/                           fakes, render helpers, msw handlers
.dependency-cruiser.cjs                               the layer gate
```

## Layer rules

`.dependency-cruiser.cjs` (run by `pnpm check`):

```js
module.exports = {
  forbidden: [
    { name: 'no-circular', severity: 'error', from: {}, to: { circular: true } },
    { name: 'no-cross-feature-internals', severity: 'error',
      from: { path: '^packages/features/([^/]+)/' },
      to: { path: '^packages/features/(?!$1)[^/]+/src/(?!index\\.ts)' } },
    { name: 'domain-is-pure', severity: 'error',
      from: { path: '/src/domain/' }, to: { path: 'react|zod|node_modules/(?!@acme/)' } },
    { name: 'application-no-adapters', severity: 'error',
      from: { path: '/src/application/' }, to: { path: '/src/(adapters|ui)/' } },
    { name: 'ui-no-adapters', severity: 'error',
      from: { path: '/src/ui/' }, to: { path: '/src/adapters/' } },
    { name: 'adapters-only-from-roots', severity: 'error',
      from: { pathNot: '^(apps/|packages/features/[^/]+/src/(adapters|index))' }, to: { path: '/src/adapters/' } },
  ],
  options: { tsConfig: { fileName: 'tsconfig.json' }, doNotFollow: { path: 'node_modules' } },
};
```

Add a rule here in the same change as any new architectural rule.

## Composition roots

```ts
// apps/api/src/app.ts
export function buildApp(deps = liveDeps()) {
  const app = fastify({ logger: false }).register(observability, deps.observability);
  app.register(ordersRoutes, { placeOrder: new PlaceOrder(deps.ordersRepo, deps.clock, deps.tracker) });
  return app;
}
```

`liveDeps()` builds adapters; tests call `buildApp(fakeDeps())`. In the
browser, `providers.tsx` builds the query client and the feature stores.

## Types as specification

- Branded ids: `type OrderId = string & { readonly __brand: 'OrderId' }` with a parser.
- zod schemas live in `adapters/` and parse at the boundary; the core receives domain types.
- Enums or literal unions instead of booleans for modes; `never` exhaustiveness in switches.
- `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes` on in `tsconfig.base.json`.

## State

- Server state through TanStack Query hooks in `ui/`; keys owned by the feature.
- Client state in one store hook per feature (Zustand `create` with immutable updates); actions named as events (`checkoutStarted`), no setters.
- Components take props and hooks; no `fetch` and no business rules inside components.

## Size

- A component above 200 lines or a use case above 120 lines is split.
- Shared code moves to `packages/core/*` when a second feature needs it.
