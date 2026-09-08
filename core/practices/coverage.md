# 100% coverage, honestly

Constitution article III. Coverage is a test of the test suite, not of the
code. The number is a tripwire for untested paths; the mutation score is the
measure of whether the tests check anything.

## The gate

- Branch coverage where the tool measures it (JaCoCo, Kover, coverlet,
  cargo-llvm-cov nightly, vitest v8, coverage.py branch, xccov regions); line
  coverage otherwise, stated as such.
- Threshold 100 in the check command, per file where the tool allows it.
- Tests, generated code and the composition root are excluded from the
  denominator by pattern in the tool config; everything else only by an in-code
  marker with a reason on the same line.
- The report is written where the agent can read it (`coverage/lcov.info`,
  `coverage.xml`, `lcov`), and the check command prints the uncovered lines.

## Exclusion markers

| Stack | Marker |
|---|---|
| kotlin-android, java-spring | `@Generated` or a Kover / JaCoCo class filter for generated code only |
| swift-ios | none official; keep the uncovered branch out of the target or document it in the file |
| dart-flutter | `// coverage:ignore-line` / `// coverage:ignore-start` with a reason |
| go | `//go:generate` output excluded by path; no line pragma - restructure instead |
| rust | `#[cfg_attr(coverage_nightly, coverage(off))]` with a reason |
| typescript-web | `/* v8 ignore next -- reason */` or `/* istanbul ignore next -- reason */` |
| python | `# pragma: no cover  # reason` |
| csharp-dotnet | `[ExcludeFromCodeCoverage(Justification = "...")]` |

A marker without a reason fails review. Grep for markers is part of review.

## Mutation testing

| Stack | Tool |
|---|---|
| kotlin-android, java-spring | PIT (pitest) |
| swift-ios | Muter |
| dart-flutter | mutation_test package |
| go | gremlins |
| rust | cargo-mutants |
| typescript-web | Stryker |
| python | mutmut |
| csharp-dotnet | Stryker.NET |

Run on the core packages in CI (nightly or on the main branch). A falling
mutation score with stable coverage means assertion-free tests were added.

## UI coverage

Line coverage on UI code comes from component tests (Compose test rule, widget
tests, Testing Library, XCTest with previews). Visual regressions use the
golden layer: Roborazzi, swift-snapshot-testing, alchemist, Playwright
screenshots, Verify. Goldens are generated in CI, not committed from a workstation.

## Adopting an existing repository

Start at the current number and ratchet: the check command fails if coverage
drops below the recorded value, and new files must be 100%. Move the recorded
value up with each change until it reads 100. A greenfield project starts at 100.

## Agent rules

- A change without tests for its new branches is incomplete.
- Error-handling paths are the most under-tested code in agent PRs; write the
  failure-case test first.
- Do not add tests for constants, for removed code, or to raise a number.
- Never lower the threshold or add an exclusion to pass the gate. Ask.

## Evidence

VGV and SQLite for the policy and its cost; Fowler, Seemann and Codecov for the
counter-case and what makes the number honest; the agentic-PR coverage study;
cargo-mutants and Test Double on mutation testing. [../evidence.md](../evidence.md), D10.
