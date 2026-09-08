# Observability - TypeScript / web

Rules in `CONSTITUTION.md` article IV.

## The canonical event

`packages/core/observability/src/event.ts`:

```ts
export type CanonicalEvent = {
  name: string;                 // 'http.request', 'page.view', 'orders.place'
  traceId: string; spanId: string;
  outcome: 'ok' | 'error' | 'cancelled';
  errorType?: string;           // class name or code, never the message
  durationMs: number;
  userId?: string;              // hashed
  sessionId: string;
  attrs: Record<string, string | number | boolean>;
};
```

Server: the Fastify plugin in `observability/src/fastify.ts` starts a span in
`onRequest`, exposes `request.observe.add(key, value)`, and emits the event in
`onResponse` and `onError` (both paths). Jobs use `observedJob(name, fn)`.
Browser: the TanStack Router `onLoad`/`onLeave` pair emits `page.view` with
time on page; use cases call `observe(name, fn)`.

Tests: `canonical-event.test.ts` uses `buildApp(fakeDeps())` with `inject` and
asserts one event with `outcome: 'ok'` for 200 and `outcome: 'error'` plus
`errorType` for a throwing route.

## Logger

Server (`observability/src/logger.ts`):

```ts
export const logger = pino({ level, redact: { paths: ['req.headers.authorization', '*.password', '*.token', '*.secret', '*.body', '*.content'], censor: '[redacted]' } });
export const requestLogger = (traceId: string) => logger.child({ trace_id: traceId });
```

Browser: `log.info(msg, fields)` facade that buffers and ships with the
events. `console.*` is banned by Biome:

```json
{ "linter": { "rules": { "suspicious": { "noConsole": "error" }, "style": { "noRestrictedGlobals": { "level": "error", "options": { "deniedGlobals": ["Date", "Math"] } } } } } }
```

(with an override allowing `Date`/`Math` inside `packages/core/clock`). Levels:
`debug` (dev), `info`, `warn` only if actionable, `error` with `error.type`.

## Privacy

- Never log tokens, message bodies or free text; ids are fine.
- pino `redact` paths above; the browser facade applies the same key list.
- Request bodies are never logged; sizes and content types are.

## Usage statistics

```ts
// packages/core/analytics/src/events.ts
export type AnalyticsEvent =
  | { name: 'checkout_started'; itemCount: number }        // owner: growth, funnel step 1
  | { name: 'order_placed'; orderId: string; amountMinor: number };
export function track(event: AnalyticsEvent): void { ... } // checks consent, then the vendor SDK
```

The union is the catalogue; a string name that is not in it fails `tsc`.
Names are `object_action` snake_case, never dynamic. The vendor SDK is
importable only from `packages/core/analytics` (Biome `noRestrictedImports`).

## Performance

- Browser: `web-vitals` (`onLCP`, `onINP`, `onCLS`) reported as events;
  `performance.mark`/`measure` around app steps (`orders.render`), collected by a `PerformanceObserver` with `buffered: true`.
- Server: OpenTelemetry JS (`@opentelemetry/sdk-node`) with `@fastify/otel` and
  the pg instrumentation; the four golden signals per route from the plugin.
- Sampling: `ParentBasedSampler(TraceIdRatioBasedSampler(0.1))`, errors always;
  retention default 30 days; both in `observability/src/config.ts`.
