# Modularization

Constitution article V. A boundary the toolchain enforces beats a boundary
described in a document.

## Module types

| Type | Holds | Depends on |
|---|---|---|
| app | the composition root, navigation shell, platform entry points | features (api), core |
| feature | one vertical slice: domain, use cases, ports, adapters, UI | core; other features only through their api |
| feature api | the public surface of a feature: contracts, navigation entries, events | core |
| core | shared infrastructure: networking, persistence, design system, logging, analytics | nothing above it |
| test-support | fakes and fixtures shared by more than one consumer | core |

A feature has an `api` and an `internal` part. Other features depend on `api`
only; the app module binds `internal` to `api` at the composition root.

## When to split

Split when a directory has its own commands, its own conventions, or its own
boundaries. Thresholds that paid off in real repos: a layer-direction check
from three packages; a shared test-support package at the second consumer of a
fake; a parity table at two UI platforms. Do not create modules for symmetry.

## Per stack

| Stack | Unit | Boundary enforcement |
|---|---|---|
| kotlin-android | Gradle module (`:feature:x:api`, `:feature:x:internal`, `:core:*`) | `internal` visibility, Konsist test, convention plugins |
| java-spring | package per bounded context, or Gradle/Maven module | Spring Modulith `verify()`, ArchUnit |
| swift-ios | Swift package per feature and layer (Tuist or SPM) | compiler; a script forbids cross-feature `@testable import` |
| dart-flutter | Dart package per feature and layer, melos or Dart workspaces | pub dependencies; `import_lint` for `src/` |
| go | `internal/<feature>/{domain,app,ports,adapters}` plus `pkg/` for shared infra | `internal` visibility, go-arch-lint |
| rust | workspace crate per feature and layer | Cargo dependencies; `cargo-modules` |
| typescript-web | package per feature in a pnpm workspace, or `src/features/<x>` with lint | dependency-cruiser, Nx `enforce-module-boundaries`, eslint `import/no-restricted-paths` |
| python | package per bounded context under `src/` | import-linter layers and independence contracts |
| csharp-dotnet | project per module | project references, ArchUnitNET |

## Rules

- Cross-module imports go through the published entry point, never a deep path.
- No circular dependencies; the gate rejects them.
- A legacy module is a migration target: no new logic goes in; do not replicate
  its patterns elsewhere.
- Module structure changes are a decision (ADR), not a side effect of a task.

## Evidence

Android's modularization guide, Thunderbird's api/internal split, VGV's
package-per-layer FFCA, Spring Modulith, feature-sliced design,
bulletproof-react, the house baseline's size thresholds.
[../evidence.md](../evidence.md), D12.
