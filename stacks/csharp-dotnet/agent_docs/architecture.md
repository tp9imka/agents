# Architecture - C# / .NET

A modular monolith: a project per module and layer, boundaries enforced by
project references and ArchUnitNET.

## Solution map

```
src/Host/Program.cs                                   composition root: builder, module registrations, ValidateOnBuild, middleware order
src/Modules/<Module>/<Module>.Contracts/              public records, interfaces and integration events other modules may reference
src/Modules/<Module>/<Module>.Domain/                 entities, value objects, strongly typed ids, invariants, domain errors; no framework packages
src/Modules/<Module>/<Module>.Application/            use cases (one class per command or query), ports (interfaces), results
src/Modules/<Module>/<Module>.Infrastructure/         EF Core DbContext and entities, repositories, clients, ModuleRegistration.cs
src/Modules/<Module>/<Module>.Api/                    minimal API endpoint groups, request and response records, error mapping
src/Shared/Observability/                             CanonicalEvent, middleware, Observe, Otel.cs, RedactingProcessor
src/Shared/Analytics/                                 AnalyticsEvent records, ITracker
src/Shared/Kernel/                                    base types used by every module; references nothing
tests/<Module>.Tests/, tests/Integration.Tests/, tests/Architecture.Tests/, tests/TestSupport/
Directory.Build.props                                 TreatWarningsAsErrors, Nullable, analyzers, BannedSymbols
Directory.Packages.props                              central package versions
```

## Layer rules

`tests/Architecture.Tests/LayerRules.cs` (ArchUnitNET, run by the check target):

```csharp
private static readonly Architecture Arch = new ArchLoader().LoadAssemblies(/* all src assemblies */).Build();
IObjectProvider<IType> Domain = Types().That().ResideInNamespace("Acme.Modules.*.Domain", true);
IObjectProvider<IType> Application = Types().That().ResideInNamespace("Acme.Modules.*.Application", true);
IObjectProvider<IType> Infra = Types().That().ResideInNamespace("Acme.Modules.*.(Infrastructure|Api)", true);

[Fact] public void DomainDependsOnNothing() =>
    Types().That().Are(Domain).Should().NotDependOnAny(Application).AndShould().NotDependOnAny(Infra).Check(Arch);
[Fact] public void ApplicationDoesNotDependOnInfra() =>
    Types().That().Are(Application).Should().NotDependOnAny(Infra).Check(Arch);
[Fact] public void EntitiesStayInInfrastructure() =>
    Classes().That().HaveNameEndingWith("Entity").Should().ResideInNamespace("Acme.Modules.*.Infrastructure", true).Check(Arch);
[Fact] public void NoServiceLocator() =>
    Classes().That().ResideInNamespace("Acme.Modules", true).Should().NotDependOnAny(typeof(IServiceProvider)).Check(Arch);
[Fact] public void ModulesTalkThroughContracts() =>
    Types().That().ResideInNamespace("Acme.Modules.Orders", true).Should()
        .NotDependOnAny(Types().That().ResideInNamespace("Acme.Modules.Users", true).And().DoNotResideInNamespace("Acme.Modules.Users.Contracts", true)).Check(Arch);
```

`PackageRules.cs` reads each `*.Domain.csproj` and fails on any
`PackageReference` outside an allow list. Add a rule in the same change as
any new architectural rule.

## Registration and wiring

```csharp
// <Module>.Infrastructure/ModuleRegistration.cs
public static IServiceCollection AddOrdersModule(this IServiceCollection s, IConfiguration cfg) => s
    .AddDbContext<OrdersDbContext>(o => o.UseNpgsql(cfg.GetConnectionString("orders")))
    .AddScoped<IOrdersRepository, EfOrdersRepository>()
    .AddScoped<PlaceOrder>();
// src/Host/Program.cs
builder.Services.AddServiceDefaults().AddOrdersModule(builder.Configuration).AddUsersModule(builder.Configuration);
builder.Host.UseDefaultServiceProvider(o => { o.ValidateOnBuild = true; o.ValidateScopes = true; });
```

Constructor injection everywhere; `IServiceProvider` is never injected into
module code. `ValidateOnBuild` makes a missing registration a startup failure
and `HostSmokeTests` a `check` failure.

## Endpoint contract

1. `MapGroup("/orders")` per module in `<Module>.Api`; one handler method per endpoint.
2. Bind a request record; validate with FluentValidation via an endpoint filter.
3. Map to a command; call one use case; return `TypedResults` (`Ok<T>`, `ValidationProblem`, `NotFound`).
4. Domain errors map to RFC 9457 problem details in `ProblemDetailsMapper`.
5. EF entities never appear in a handler or a response.

## Types as specification

- `readonly record struct OrderId(Guid Value)` for every id; `record` for commands, queries and results.
- Nullable reference types on; warnings are errors; `required` members instead of nullable-then-check.
- Enums instead of booleans for modes; exhaustive `switch` expressions.

## Size

- A use case above 150 lines or an endpoint group above 250 lines is split.
- Shared code moves to `src/Shared/*` only when a second module needs it.
