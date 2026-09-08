# AGENTS.md - <Project> (Dart / Flutter)

<Project> is a Flutter app: Dart <3.x>, Flutter <3.x> pinned in `.fvmrc`,
feature-first packages in a melos workspace, bloc/Cubit for state, get_it +
injectable for dependencies, go_router for navigation, drift or sqflite for
persistence, dio behind a port. The seven articles of `CONSTITUTION.md`
apply; each names its gate below.

## Commands

- Setup: `fvm install && fvm dart pub global activate melos && melos bootstrap`. Always `fvm flutter` / `fvm dart`, never the global SDK.
- Check (the CI gate): `melos run check` - `dart format --set-exit-if-changed`, `dart analyze --fatal-infos`, `import_lint`, `build_runner` drift check, `very_good test --coverage --min-coverage 100 --test-randomize-ordering-seed random` per package, golden verification.
- Run: `fvm flutter run --flavor dev -t lib/main_dev.dart`
- Test one package: `cd packages/features/orders && fvm flutter test --coverage`
- Test one file or test: `fvm flutter test test/orders_cubit_test.dart` / `--plain-name 'emits error when network fails'`
- Format and analyze one package: `fvm dart format . && fvm dart analyze --fatal-infos`
- Codegen: `melos run gen` (injectable, freezed, drift). Generated files are never edited.
- Goldens: `fvm flutter test --update-goldens` only in CI on `main`; locally run `melos run test:goldens` to verify.
- Iterate with the package's `flutter test`; run `melos run check` before declaring done.

## Architecture

- Feature-first packages (FFCA): `packages/features/<name>/{<name>_domain,<name>_data,<name>_ui}` plus `packages/core/*`; apps under `apps/` compose features. A feature package never depends on another feature's data or ui package; cross-feature calls go through the feature's domain contracts or events. Gate: pub dependencies (a package boundary is enforced by the compiler) plus `import_lint` rules in `analysis_options.yaml`.
- Dependency rule inside a feature: `domain` <= `data` <= `ui`. `domain` depends on no Flutter package (`flutter:` is absent from its `pubspec.yaml`). Gate: `import_lint` and the pubspec.
- DI: get_it + injectable; constructor injection only; `configureDependencies()` in `apps/<app>/lib/injection.dart` is the composition root. `getIt<T>()` is called only there and in `main`. Gate: `import_lint` forbids `get_it` imports outside `injection.dart` and tests.
- UI: bloc/Cubit per screen with immutable freezed states; widgets render state and add events; side effects only through use cases. Gate: `bloc_lint` plus review.
- Generated code (`*.g.dart`, `*.freezed.dart`, `*.config.dart`) is never edited; `melos run gen` then `git diff --exit-code` runs in `check`.
- Layout and rules in full: `agent_docs/architecture.md`.

## Testing

- Test-first: the failing test comes first; a change whose tests pass with it stashed is not done. Gate: review runs `git stash && melos run test` on the diff; no Dart TDD hook exists yet.
- Coverage: `very_good test --min-coverage 100` per package fails below 100% line coverage. Exclusions only via `// coverage:ignore-line` or `-start`/`-end` with a reason on the same line; generated files are excluded by pattern in `melos.yaml`.
- Tests: `test` + `bloc_test` for cubits, `mocktail` only for third-party boundaries, fakes for own ports in `packages/core/test_support`, widget tests with `pumpApp` from `test_support`, goldens with alchemist per screen state.
- Mutation: `mutation_test` on `packages/features/*_domain` nightly; a score under 80% fails.
- Time and randomness are injected (`Clock`, `Random`); `DateTime.now()` in `lib/` is forbidden. Gate: custom lint `no_datetime_now` in `packages/core/lints`.
- Recipes: `agent_docs/testing.md`.

## Observability

- Every screen visit and every use-case call emits one canonical event through `packages/core/observability` (`CanonicalEvent`: `event.name`, `trace_id`, `outcome`, `error.type`, `duration_ms`, `user.id`, business fields). `ObservedUseCase` and the `ObservedRoute` observer emit it in `finally`; feature code cannot skip it. Gate: `canonical_event_test.dart` per feature.
- Logging: `packages/core/observability/Log` only (wraps `logging` and the Sentry logger). `print`, `debugPrint` and `developer.log` are forbidden. Gate: `avoid_print` plus custom lint `no_debug_print`.
- Levels: `fine` (dev only), `info`, `severe` with `error.type`. A `warning` must be actionable.
- Privacy: never log tokens, message bodies or free text; ids are fine. `SentryOptions.beforeSend` and the OTel processor in `otel_config.dart` redact `password|token|secret|body|content`.
- Usage events: `packages/core/analytics/analytics_event.dart` (a sealed class) is the catalogue; names `object_action` snake_case; `Tracker.track(AnalyticsEvent)` only. Gate: custom lint `analytics_catalogue_only`.
- Performance: Sentry Flutter for app start, slow and frozen frames, screen load and navigation spans; spans from `ObservedUseCase` via opentelemetry-dart (traces beta, no logs) exported OTLP; Firebase Performance optional. Sampling and retention in `otel_config.dart`.
- Setup and fields: `agent_docs/observability.md`.

## Boundaries

- Always: run the package's tests after each change and `melos run check` before saying done; regenerate with `melos run gen` after touching an annotated class; add an `import_lint` rule when you add an architectural rule; put new code in a feature or core package, never in `apps/` except wiring and routes.
- Ask first: adding a dependency to any `pubspec.yaml`; adding or splitting a package; bumping the Flutter version in `.fvmrc`; changing a feature's domain contract; editing `melos.yaml` or `.github/workflows/`.
- Never: commit secrets or `*.env` files (use `env.example` and `--dart-define-from-file`); edit generated `*.g.dart` / `*.freezed.dart` / `*.config.dart` (regenerate); disable, delete or weaken a failing test (ask); use `print` or `debugPrint` (use `Log`); call `getIt<T>()` outside `injection.dart` (inject through the constructor); put business logic in a widget (use a Cubit and a use case).

## Where to look

- `agent_docs/architecture.md` - package map, layer rules, injectable setup, routing
- `agent_docs/testing.md` - bloc_test, widget tests, alchemist goldens, coverage config, mutation
- `agent_docs/observability.md` - canonical event, logger, catalogue, Sentry and OTel setup, privacy
- `agent_docs/gates.md` - what `melos run check` runs, CI, hooks
- Exemplars: `packages/features/orders/orders_ui/lib/src/order_cubit.dart`, `packages/features/orders/orders_data/lib/src/orders_repository_impl.dart`, `packages/features/orders/orders_ui/test/order_cubit_test.dart`
- Legacy: none. When a legacy package appears, list it here and do not copy its patterns.

## Maintaining this file

- Add a line only after an observed failure, then re-run the task without and with the line and keep it only if the outcome changed. Every rule names its gate or its reason. Revisit after model releases. Stay under 150 lines.
