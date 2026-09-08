# Architecture principles

Constitution article V. The same shape in every stack, with the stack's own
words and its own gate.

## The dependency rule

Source dependencies point inward. The domain knows nothing of the
application layer; the application layer knows nothing of adapters; adapters
know nothing of each other. Data crossing a boundary is plain: values,
records, DTOs; never an entity from an outer ring, never a framework type in
the core.

## Vocabulary

| Term | Meaning |
|---|---|
| domain | entities, value objects, domain services, invariants; no I/O, no framework |
| application | use cases and handlers that orchestrate the domain through ports |
| port | an interface the core owns: driving (called by the outside) or driven (calls the outside) |
| adapter | an implementation of a port: HTTP, UI, database, queue, SDK |
| composition root | the one place adapters are bound to ports; `main`, the app module, the DI module |
| feature | a vertical slice: its own domain, application, ports and adapters, in its own module |

Tests drive the primary ports the same way the UI does. If a feature cannot be
tested through its ports without a device or a network, the boundary is wrong.

## Feature-first, then layers

Organise by feature first, layers inside the feature. A feature module never
imports another feature's internals; it imports the other feature's published
API (its `:api` module, its package's public surface) or communicates by
events. Shared code lives in core modules that features depend on and that
depend on no feature.

Split into a new module when a directory has different commands, different
conventions or different boundaries. Do not split for symmetry.

## Rules that survive contact with agents

- Keep important checks local. Permission, validation and invariants live where
  the reader sees them, not in a config file or a distant base class.
- Prefer functions with descriptive names over class hierarchies. No inheritance
  for reuse.
- Explicit over clever: plain SQL over a maxed-out ORM, plain data over magic.
- Errors are values at the ports; adapters translate; nothing swallows an
  error silently.
- Modules have a size. Above roughly 500 lines of non-test code, add a module;
  above 800, stop extending.
- Document only what the code does today. An aspirational pattern in the
  instruction file gets implemented prematurely and inconsistently.

## The gate

Every stack template ships a layer gate in the check command (see
[../practices/gates.md](../practices/gates.md)) and a composition-root smoke
test that builds the whole graph.

## Evidence

Martin's dependency rule, Cockburn's ports and adapters, Graca's explicit
architecture, the domain-driven-hexagon guide, VGV's feature-first clean
architecture, Thunderbird's api/internal split, the Android modularization
guide, Bogard's vertical slices, Ronacher's agent-legibility rules, Codex's
module size rule. [../evidence.md](../evidence.md), D12.
