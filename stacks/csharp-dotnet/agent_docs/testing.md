# Testing - C# / .NET

Rules in `CONSTITUTION.md` articles II and III.

## Workflow

1. Name the projects and types the change touches, in the task.
2. List the tests with behaviour names: `ReturnsErrorWhenCartIsEmpty`, `PersistsOrderAndPublishesEvent`.
3. Per test: write it, run `dotnet test tests/Orders.Tests --filter "FullyQualifiedName~PlaceOrderTests.<name>"`, see it fail for the right reason, implement the minimum, run the project, refactor green.
4. Structural commits separate from behavioural ones.
5. Before done: the check target; every project touched reads 100% branch and line.

## Test types

| Level | Tool | Location |
|---|---|---|
| unit (domain, use cases) | xUnit `[Fact]` / `[Theory]` with `[InlineData]`, FluentAssertions | `tests/<Module>.Tests` |
| endpoint | `WebApplicationFactory<Program>` with fakes registered over the live services | `tests/<Module>.Tests` |
| persistence | Testcontainers Postgres, real `DbContext`, migrations applied | `tests/Integration.Tests` |
| snapshot | Verify for serialised responses, updated with intent | `tests/<Module>.Tests` |
| architecture | ArchUnitNET, `PackageRules` | `tests/Architecture.Tests` |

Fakes for own ports live in `tests/TestSupport` (`InMemoryOrdersRepository`,
`FakeTimeProvider` from `Microsoft.Extensions.TimeProvider.Testing`,
`RecordingTracker`). NSubstitute only for third-party clients.

## Coverage gate

`Directory.Build.targets` (applies to every test project):

```xml
<PropertyGroup>
  <CollectCoverage>true</CollectCoverage>
  <CoverletOutputFormat>cobertura</CoverletOutputFormat>
  <Threshold>100</Threshold>
  <ThresholdType>branch,line</ThresholdType>
  <ThresholdStat>minimum</ThresholdStat>
  <ExcludeByAttribute>GeneratedCodeAttribute,ExcludeFromCodeCoverageAttribute,CompilerGeneratedAttribute</ExcludeByAttribute>
  <ExcludeByFile>**/Migrations/*.cs,**/Program.cs,**/*.g.cs</ExcludeByFile>
</PropertyGroup>
```

Exclusions in code only: `[ExcludeFromCodeCoverage(Justification = "reason")]`;
a missing `Justification` fails review. Never lower `Threshold`; never add a
hand-written file to `ExcludeByFile`.

## Mutation

`stryker-config.json` with `"mutate": ["src/Modules/**/*.Domain/**", "src/Modules/**/*.Application/**"]`,
`"thresholds": { "high": 90, "low": 80, "break": 80 }`; `dotnet stryker` in `nightly.yml`.

## Rules

- `TimeProvider` is injected everywhere; `DateTime.Now`, `DateTime.UtcNow`, `DateTimeOffset.UtcNow`, `Random.Shared` are in `BannedSymbols.txt`.
- Failure path first: every domain error and every problem-details response has a test.
- No tests for constants, no assertion-free tests, no `Skip =` without a linked task.
- Structured log assertions through `FakeLogger` (`Microsoft.Extensions.Diagnostics.Testing`), never substring matches on rendered text.
- Verify snapshots are scrubbed (dates, ids) and updated only with a reviewed diff.
