# Observability - C# / .NET

Rules in `CONSTITUTION.md` article IV.

## The canonical event

`src/Shared/Observability/CanonicalEvent.cs` (a record): `Name`, `TraceId`,
`SpanId`, `Outcome` (Ok, Error, Cancelled), `ErrorType`, `DurationMs`,
`UserId` (hashed), `Attributes` (dictionary).

`CanonicalEventMiddleware` is registered first in `Program.cs`: it reads
`Activity.Current` for ids, stores an `EventBuilder` in `HttpContext.Items`,
and emits the event in `finally` as one `ILogger` record with all properties
(`LogInformation` or `LogError`). Handlers add fields with
`Observe.Add(context, "order.id", id)`; background jobs use `Observe.Job("name", ...)`.

Tests: `CanonicalEventTests` with `WebApplicationFactory` and `FakeLogger`
assert one event with `outcome=Ok` for a 200 and `outcome=Error` plus
`error.type` for a throwing endpoint.

## Logging

`ILogger<T>` with message templates:

```csharp
_logger.LogInformation("order placed {OrderId}", order.Id);
_logger.LogError(ex, "place failed {ErrorType}", ex.GetType().Name);
```

Never `$"..."` interpolation in a log call (CA2254), never `Console.Write*`.
`BannedSymbols.txt`:

```
M:System.Console.WriteLine;Use ILogger<T>
M:System.Console.Write;Use ILogger<T>
P:System.DateTime.Now;Inject TimeProvider
P:System.DateTime.UtcNow;Inject TimeProvider
P:System.DateTimeOffset.UtcNow;Inject TimeProvider
P:System.Random.Shared;Inject a random port
```

Levels: `Debug` (dev), `Information`, `Warning` only if actionable, `Error`
with `error.type`. Aspire service defaults export logs through OpenTelemetry;
Serilog compact JSON to the console in development.

## Privacy

- Never log tokens, message bodies or free text; ids are fine.
- `RedactingProcessor` (an OpenTelemetry `BaseProcessor<LogRecord>`) in
  `Otel.cs` drops attributes named `password|token|secret|body|content|authorization`.
- Request bodies are never logged; sizes and content types are.

## Usage statistics

```csharp
public abstract record AnalyticsEvent(string Name);
/// owner: growth - funnel step 1
public sealed record CheckoutStarted(int ItemCount) : AnalyticsEvent("checkout_started");
public interface ITracker { void Track(AnalyticsEvent e); }   // checks consent
```

Names are `object_action` snake_case, never dynamic. ArchUnitNET forbids the
vendor SDK outside `Shared/Analytics`.

## Performance

- `AddServiceDefaults()` (Aspire) wires OpenTelemetry traces, metrics and
  logs with the OTLP exporter; `AddAspNetCoreInstrumentation`,
  `AddHttpClientInstrumentation`, `AddNpgsql()` on the tracer.
- Golden signals per endpoint from `http.server.request.duration` and
  `http.server.active_requests`; `kestrel` connection metrics for saturation.
- `dotnet-counters` and `dotnet-trace` for profiling; `dotnet-gcdump` for memory.
- Sampling: `ParentBased(TraceIdRatioBased(0.1))`, errors always via a
  custom sampler; retention default 30 days; both in `Otel.cs`.
