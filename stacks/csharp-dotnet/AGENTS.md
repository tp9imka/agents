# AGENTS.md - <Project> (C# / .NET)

<Project> is a .NET <9> solution (`<Project>.slnx`): ASP.NET Core minimal
APIs, EF Core with Postgres, a project per module under `src/Modules/`,
`src/Host/` as the composition root, Aspire service defaults for
observability, xUnit. C# version follows `global.json`. The seven articles of
`CONSTITUTION.md` apply; each names its gate below.

## Commands

- Setup: SDK version from `global.json` (`dotnet --version` must match); `dotnet tool restore` installs Stryker, ReportGenerator and the formatters.
- Check (the CI gate): `dotnet cake --target=Check` (or `./check.sh`) - `dotnet format --verify-no-changes`, `dotnet build -warnaserror`, ArchUnitNET tests, EF migration drift check, `dotnet test` with coverlet thresholds (100% branch), public API drift.
- Build: `dotnet build`; run: `dotnet run --project src/Host`
- Test all: `dotnet test`
- Test one project, class or method: `dotnet test tests/Orders.Tests --filter "FullyQualifiedName~PlaceOrderTests.ReturnsErrorWhenCartIsEmpty"`
- Format one project: `dotnet format src/Modules/Orders`
- Coverage report: `dotnet test --collect:"XPlat Code Coverage"` then `dotnet reportgenerator -reports:**/coverage.cobertura.xml -targetdir:coverage`
- Migrations: `dotnet ef migrations add <What> --project src/Modules/Orders/Orders.Infrastructure`; never edit an applied migration.
- Integration tests (Testcontainers Postgres, needs Docker): `dotnet test tests/Integration.Tests`
- Iterate with `--filter`; run the check target before declaring done.

## Architecture

- A project per module and layer: `src/Modules/<Module>/<Module>.Domain`, `.Application`, `.Infrastructure`, `.Api` (endpoints); `<Module>.Contracts` is the only project other modules may reference. Gate: project references plus ArchUnitNET tests in `tests/Architecture.Tests` run by the check target.
- Dependency rule: `Domain` <= `Application` <= `Infrastructure`/`Api`; `Domain` references no framework package (no EF Core, no ASP.NET, no Newtonsoft). Gate: `Domain.csproj` has no such `PackageReference` (checked by `tests/Architecture.Tests/PackageRules.cs`) plus ArchUnitNET layer rules.
- DI: `Microsoft.Extensions.DependencyInjection` with constructor injection; each module registers its services in `<Module>.Infrastructure/ModuleRegistration.cs`; `src/Host/Program.cs` composes modules and calls `ValidateOnBuild`. No service locator (`IServiceProvider` injected into services). Gate: ArchUnitNET rule `NoServiceLocator`; `ValidateOnBuild = true`.
- Endpoints: minimal API groups per module mapping request records to commands, one handler per endpoint, results mapped to `TypedResults`; EF entities never cross the API boundary. Gate: ArchUnitNET rule `EntitiesStayInInfrastructure`.
- Types are the spec: records for commands and results, strongly typed ids (`readonly record struct OrderId`), nullable reference types enabled with warnings as errors. Gate: `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>` in `Directory.Build.props`.
- Generated code (public API files, EF migrations, OpenAPI clients) is never edited by hand; drift fails the check target.
- Layout and rules in full: `agent_docs/architecture.md`.

## Testing

- Test-first: the failing test comes first; a change whose tests pass with it stashed is not done. Gate: review runs `git stash && dotnet test` on the diff; no .NET TDD hook exists yet.
- Coverage: coverlet with `Threshold=100`, `ThresholdType=branch,line`, `ThresholdStat=minimum` in `Directory.Build.targets`; excludes only `Program.cs`, migrations and generated files by attribute. Exclusions in code only: `[ExcludeFromCodeCoverage(Justification = "...")]` with a reason.
- Tests: xUnit with `[Theory]` and `[InlineData]` for cases, FluentAssertions, fakes for own ports in `tests/TestSupport`, `WebApplicationFactory` for endpoints, Testcontainers for repositories, Verify for snapshot outputs, NSubstitute only for third-party clients.
- Mutation: `dotnet stryker` on `*.Domain` and `*.Application` nightly; `thresholds.break` 80 in `stryker-config.json`.
- Time and randomness are injected (`TimeProvider`, `Random.Shared` behind a port); `DateTime.Now`, `DateTime.UtcNow` and `DateTimeOffset.UtcNow` in module code are forbidden. Gate: analyzer rule `BannedApiAnalyzers` with `BannedSymbols.txt`.
- Recipes: `agent_docs/testing.md`.

## Observability

- Every request, job and message emits one canonical event through `src/Shared/Observability` (`CanonicalEvent`: `event.name`, `trace_id`, `outcome`, `error.type`, `duration_ms`, `user.id`, business fields) from `CanonicalEventMiddleware` in `finally`; handlers add fields with `Observe.Add(...)`. Gate: `CanonicalEventTests` with `WebApplicationFactory` asserts the event on 200 and on an exception.
- Logging: `ILogger<T>` with message templates and named properties, exported through OpenTelemetry (Aspire service defaults) and Serilog compact JSON in development. `Console.Write*` and string interpolation in log calls are forbidden. Gate: `BannedSymbols.txt` and analyzer CA2254.
- Levels: `Debug` (dev), `Information`, `Error` with `error.type`; a `Warning` must be actionable.
- Privacy: never log tokens, message bodies or free text; ids are fine. The `RedactingProcessor` in `Observability/Otel.cs` drops `password|token|secret|body|content|authorization`.
- Usage events: `src/Shared/Analytics/AnalyticsEvent.cs` (an abstract record hierarchy) is the catalogue; names `object_action` snake_case; `ITracker.Track(AnalyticsEvent)` only. Gate: the sealed hierarchy plus ArchUnitNET forbidding the vendor SDK outside `Shared/Analytics`.
- Performance: Aspire `ServiceDefaults` (OpenTelemetry traces, metrics and logs with OTLP export), `Microsoft.AspNetCore` and `Npgsql` instrumentation; the four golden signals per endpoint from `http.server.request.duration`; `dotnet-counters` and `dotnet-trace` for profiling. Sampling: parent-based 10%, errors always; retention default 30 days (`Observability/Otel.cs`).
- Setup and fields: `agent_docs/observability.md`.

## Boundaries

- Always: run the project's tests after each change and the check target before saying done; add an ArchUnitNET rule when you add an architectural rule; put new code in `src/Modules/<Module>/` or `src/Shared/`, never in `src/Host/` except composition.
- Ask first: adding a `PackageReference` or changing `Directory.Packages.props`; changing a `<Module>.Contracts` type; adding a module; altering an existing table in place; bumping the SDK in `global.json`; editing `Directory.Build.props`, `BannedSymbols.txt` or `.github/workflows/`.
- Never: commit secrets or `appsettings.Local.json` (use user secrets and `appsettings.Local.json.example`); edit an applied migration or a generated `PublicAPI.*.txt` by hand (regenerate); disable or delete a failing test or add `Skip =` to get green (ask); use `Console.Write*` (use `ILogger<T>`); inject `IServiceProvider` into a service (constructor injection); reference another module's non-Contracts project (use `<Module>.Contracts`); use `DateTime.Now` (inject `TimeProvider`).

## Where to look

- `agent_docs/architecture.md` - project map, ArchUnitNET rules, module registration, endpoint contract
- `agent_docs/testing.md` - xUnit patterns, fakes, WebApplicationFactory, coverlet config, Stryker
- `agent_docs/observability.md` - canonical event middleware, logging, catalogue, Aspire and OTel, privacy
- `agent_docs/gates.md` - what the check target runs, CI, hooks
- Exemplars: `src/Modules/Orders/Orders.Application/PlaceOrder.cs`, `src/Modules/Orders/Orders.Infrastructure/EfOrdersRepository.cs`, `tests/Orders.Tests/PlaceOrderTests.cs`
- Legacy: none. When a legacy project appears, list it here and do not copy its patterns.

## Maintaining this file

- Add a line only after an observed failure, then re-run the task without and with the line and keep it only if the outcome changed. Every rule names its gate or its reason. Revisit after model releases. Stay under 150 lines.
