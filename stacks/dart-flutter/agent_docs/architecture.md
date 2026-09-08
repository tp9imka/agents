# Architecture - Dart / Flutter

Feature-First Clean Architecture: every layer of every feature is a Dart
package, so the boundary is enforced by `pubspec.yaml`, not by convention.

## Package map

```
apps/<app>/                             composition root: main_<flavor>.dart, injection.dart (configureDependencies), router.dart
packages/features/<name>/
  <name>_domain/                        entities, value objects, use cases, ports (abstract classes) - no flutter: dependency
  <name>_data/                          repositories, DTOs, dio/drift adapters implementing the ports
  <name>_ui/                            cubits/blocs, freezed states, widgets, routes contributed to the app
packages/core/observability/            CanonicalEvent, Log, ObservedUseCase, ObservedRoute, otel_config.dart
packages/core/analytics/                AnalyticsEvent sealed class, Tracker port
packages/core/network/, core/database/  shared infrastructure, no feature knowledge
packages/core/design_system/            theme, tokens, components, previews
packages/core/test_support/             fakes for shared ports, pumpApp, golden helpers
packages/core/lints/                    custom_lint rules used by every package
melos.yaml                              scripts: bootstrap, gen, check, test, test:goldens
```

## Layer rules

- `<name>_domain` depends on `core/observability` (for `ObservedUseCase`) and nothing else from the app; no `flutter:` in its pubspec.
- `<name>_data` depends on `<name>_domain` and core infrastructure; never on `<name>_ui`.
- `<name>_ui` depends on `<name>_domain` (use cases, entities); never on `<name>_data`.
- Features depend on other features only through `<other>_domain` contracts or events; never on `_data` or `_ui`.
- `apps/*` are the only packages that depend on `_data` packages, to bind them.

`import_lint` in the root `analysis_options.yaml` mirrors these as rules
(`domain_no_flutter`, `ui_no_data`, `no_cross_feature_internals`) and runs in `melos run check`.

## Dependency injection

injectable over get_it:

```dart
@LazySingleton(as: OrdersPort)
class OrdersRepositoryImpl implements OrdersPort {
  OrdersRepositoryImpl(this._api, this._db, this._clock);
  ...
}
@injectable
class PlaceOrder extends ObservedUseCase<Cart, OrderId> {
  PlaceOrder(this._orders, Tracker tracker) : super('orders.place', tracker);
}
```

`apps/<app>/lib/injection.dart` holds `@InjectableInit(...)` and
`configureDependencies(Env)`; environments select adapters (`@dev`, `@prod`).
Nothing outside `injection.dart`, `main_*.dart` and tests imports `get_it`.
`injection_test.dart` builds the graph for every environment so a missing
binding fails `check`.

## State

- One Cubit per screen owning a freezed `State` (`initial`, `loading`, `loaded`, `failure(errorType)`); events are Cubit methods or bloc events named as facts.
- Cubits call use cases only; no dio, drift or `Navigator` in a Cubit.
- Widgets are `StatelessWidget` reading state with `BlocBuilder`; local UI state only in `StatefulWidget`.
- Navigation with go_router; routes are contributed by `_ui` packages and assembled in `apps/<app>/lib/router.dart`.

## Size and placement

- A Cubit above 200 lines or a use case above 100 lines is split.
- Shared code moves to `packages/core/*` when a second feature needs it, not before.
