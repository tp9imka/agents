# The source is the specification

Constitution article I. This is the collection's position on "spec-driven
development" and it differs from most tools that use the term.

## Vocabulary

Three levels exist in the wild:

- Spec-first: a spec is written before the task and used during it.
- Spec-anchored: the spec is kept after the task and maintained.
- Spec-as-source: humans edit only the spec; code is generated.

This collection is spec-first, and the anchored artifact is the code and its
tests. There is no separate document to keep in sync, so nothing drifts.

## What replaces the documents

| Document elsewhere | Here |
|---|---|
| requirements.md, PRD | a checklist of tests, in the task |
| design.md | the types, ports and module layout, plus an ADR if a decision was made |
| tasks.md | the same checklist, ordered, with `depends:` annotations where needed |
| acceptance criteria | executable examples: doctests, spec-style test suites, fixture tests |

Kept: a short versioned `CONSTITUTION.md` (process, not features) and ADRs
under `docs/adr/` for decisions with alternatives.

## Types are specification

Parse at the boundary into domain types that make invalid states
unrepresentable. Inside the core, functions take and return those types;
no strings for identifiers, no booleans for modes (use enums), no nullable
fields that are "never actually null". The compiler then checks part of the
spec on every build.

## Executable examples per stack

| Stack | Spec-shaped tests |
|---|---|
| kotlin-android, java-spring | kotest BehaviorSpec / FeatureSpec, JUnit 5 `@Nested` + `@DisplayName` |
| swift-ios | swift-testing `@Suite` with `@Test(arguments:)`, TCA `TestStore` |
| dart-flutter | `group` / `test` with behaviour names, `bloc_test` state sequences |
| go | table-driven tests named by scenario, `Example_` functions |
| rust | doctests on every public item, `#[cfg(test)]` modules, proptest |
| typescript-web | Vitest `describe` / `it` by behaviour, fast-check properties |
| python | doctest for pure functions, pytest parametrize, Hypothesis |
| csharp-dotnet | xUnit `[Theory]`, Verify snapshots for outputs |

## When asked for a spec

Produce, in this order, and nothing else:

1. The shape: modules and types touched, ports crossed, one paragraph.
2. The checklist of tests with behaviour names, ordered so each can be red then green.
3. An ADR only if a decision between alternatives was made.

## Why

Prose specs drift from code within days; the document stack of the
spec-driven tools reintroduces waterfall handoffs; agents follow the file they
are given literally, so the file must be the executable one. See
[../evidence.md](../evidence.md), D9.
