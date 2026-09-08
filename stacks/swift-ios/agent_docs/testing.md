# Testing - Swift / iOS

Rules in `CONSTITUTION.md` articles II and III; this page is how they run here.

## Workflow

1. Name the packages and types the change touches, in the task.
2. List the tests as a checklist with behaviour names: `placesOrderWhenCartIsValid`, `showsErrorWhenNetworkFails`.
3. Per test: write it, run `swift test --package-path Packages/Orders --filter OrderModelTests/<name>`, see it fail for the right reason, implement the minimum, run the package, refactor green.
4. Structural commits separate from behavioural ones.
5. Before done: `make check`; the coverage gate must read 100 for every package touched.

## Test types

| Level | Tool | Location |
|---|---|---|
| unit (domain, use cases, screen models) | swift-testing: `@Suite`, `@Test`, `#expect`, `@Test(arguments:)` | `Packages/<Feature>/Tests` |
| adapter | swift-testing with `URLProtocol` stubs and an in-memory store | `Packages/<Feature>/Tests` |
| screen | snapshot tests per `State` with swift-snapshot-testing; previews generate the cases | `Packages/<Feature>/Tests` |
| UI flow | XCTest UI tests, few | `App/UITests`, nightly |

Fakes for shared ports live in `Packages/TestSupport`. Override with
`withDependencies { $0.orders = .fake(...) }`; an unstubbed key fails the test
because `testValue` is `unimplemented`.

## Coverage gate

`Scripts/coverage-gate.sh` (in `make check`):

```bash
xcodebuild test -scheme App -enableCodeCoverage YES -resultBundlePath build/result.xcresult -quiet
xcrun xccov view --report --json build/result.xcresult > build/coverage.json
python3 Scripts/coverage_check.py build/coverage.json --min 100 --exclude 'Tests/,Previews/,App/AppDependencies.swift,DesignSystem/Previews/'
```

`coverage_check.py` prints uncovered regions per file and exits 1 below the
minimum. There is no per-line pragma in Swift: an unreachable branch is
removed, or the file carries a comment above it explaining why the region
stays uncovered and the file is listed in `--exclude` with that reason in the
script. Never lower `--min`.

## Mutation

`muter` on `Packages/*` in `.github/workflows/nightly.yml`, threshold 80 in
`muter.conf.yml`. A falling score with stable coverage means assertion-free tests.

## Snapshots

`assertSnapshot(of: OrderView(model: .preview(.loaded)), as: .image(layout: .device(config: .iPhone13)))`
per state. Goldens are recorded on CI from `main` with `SNAPSHOT_RECORD=1`;
never from a workstation.

## Rules

- Dates, UUIDs and randomness through `@Dependency(\.date)`, `\.uuid`, `\.withRandomNumberGenerator`.
- Failure path first: every thrown error and every `.failure` state has a test.
- No tests for constants, no assertion-free tests, no `try!` in tests.
- One behaviour per test, named as a sentence in camelCase.
- Flaky tests get `.disabled("flaky: <task>")` with a linked task, not deletion.
