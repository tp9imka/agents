# Unidirectional flow

For UI stacks. State flows down, events flow up, and every transition is a
test.

```
UI  =>  events / actions  =>  state holder  =>  immutable state  =>  UI
```

## Rules

- The UI is a projection of state. It renders and translates user input into
  events. No business logic, no I/O in the view.
- One state holder per screen or feature owns an immutable state value and is
  the single source of truth for it. Derived values are computed, not stored.
- Events are named as facts (`SubmitTapped`, `OrderLoaded`), not as setters.
  Many handlers may react to one event.
- Side effects run outside the reducer: in workers, effects, use cases. The
  state holder calls ports; it never touches SDKs directly.
- State and events are serialisable values: no closures, no framework objects.
- Every transition has a test: given state and event, expect state (and effects).

## Per stack

| Stack | Pattern | State holder | Transition tests |
|---|---|---|---|
| kotlin-android | UDF with `ViewModel` + `StateFlow`, Orbit MVI for typed side effects | ViewModel | Turbine on the flow; `testRender`-style for Workflow |
| swift-ios | `@Observable` model per screen, or TCA reducers | model / `Store` | TCA `TestStore` exhaustive assertions; plain XCTest on models |
| dart-flutter | bloc / Cubit | Bloc | `bloc_test` `expect` state sequences |
| typescript-web | Redux Toolkit or a store hook per feature; server state in TanStack Query | slice / store | reducer tests; Testing Library for components |
| csharp-dotnet (MAUI) | MVVM with immutable state records | ViewModel | xUnit on the ViewModel |

## Anti-patterns

- Mutable state shared between screens through a global.
- Dispatching several events in a row to reach one state; model the intent once.
- Logic in the view because "it is just formatting"; formatting is derived state.

## Evidence

The Redux style guide's essential rules, Android's UI-layer guide, bloc,
TCA's TestStore, Orbit. [../evidence.md](../evidence.md), D14.
