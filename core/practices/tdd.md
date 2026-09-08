# Test-first

Constitution article II. Applies to features, bug fixes, refactors and behaviour
changes. Exceptions, each needing a human's yes: throwaway prototypes,
generated code, configuration files.

## The rule

No production code without a failing test first. If the code exists before the
test, delete it and implement again from the test. Do not keep it as reference.

## The workflow

1. Design the shape. Name the modules and types the change touches and where
   the ports are. Two minutes, written in the task description, not a document.
2. List the tests as a checklist. This list is the specification. For a bug,
   the first entry reproduces it.
3. For each entry: write the test, run it, confirm it fails for the right reason
   (a missing behaviour, not a syntax error), write the minimum to pass, run the
   whole suite, refactor with the suite green.
4. Separate structural commits (rename, move, extract) from behavioural ones.
   Never mix them.
5. Commit only when all tests pass, all warnings are resolved, and the change is
   one logical unit.

## Definition of done

- Every changed or added behaviour has a test, and every new test fails when the
  change is stashed. Reviewers may run `git stash && <test command>` to verify.
- Coverage of the diff is 100% (see [coverage.md](coverage.md)).
- The check command passes locally; CI runs the same command.
- No test was disabled, skipped, deleted or loosened. If one had to be, the
  reason is in the change description and a human approved it.

## What agents get wrong

Watch for and refuse:

- Implementation first, tests generated after, red never observed.
- Assertion-free tests or tests that only call the function.
- Tests for statically defined values, or negative tests for code that was removed.
- Disabling a test, widening a tolerance, or changing an expected value to pass.
- Functionality nobody asked for, with tests to match.
- Loops: the same failing edit repeated. Stop and narrow the scope.

## Enforcers per stack

| Stack | Deterministic hook | Fallback |
|---|---|---|
| typescript-web | tdd-guard / Probity (Vitest, Jest) | diff rule in review |
| python | tdd-guard / Probity (pytest) | diff rule |
| go | tdd-guard / Probity (go test) | diff rule |
| rust | tdd-guard / Probity (cargo test) | diff rule |
| kotlin-android, java-spring | none yet | diff rule; coverage of diff = 100%; PR check that changed files have changed tests |
| swift-ios | none yet | same as Kotlin |
| dart-flutter | none yet | same as Kotlin; `very_good test --coverage` |
| csharp-dotnet | none yet | same as Kotlin |

Where no hook exists, the coverage gate plus the diff rule is the enforcement;
the hook is added the day a reporter exists for the stack.

## Test shape

- Test behaviour through the public surface of a module, not private methods.
- One level per behaviour: unit for logic, component or widget for UI state,
  integration for the seams, few end-to-end. If a higher test catches a bug no
  lower test caught, add the lower test.
- Prefer real collaborators in a temp directory or container over mocks of
  your own code; fake only the boundary you do not own.
- Name tests by behaviour: `returns_error_when_email_is_invalid`.
- Keep tests dense: one focused case beats a broad fixture.
- Property-based tests for pure functions with a non-trivial input space.

## Evidence

Kent Beck's system prompt and Iron Law wording; the Airflow diff rule; the
Fowler-site experiment that found strict in-loop red-green no better than
test-first with a design step; Dan Luu's 26-condition comparison; the
agentic-PR study showing agents test half their changes. Records in
[../evidence.md](../evidence.md), D8.
