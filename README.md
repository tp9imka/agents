# agents

`AGENTS.md` templates by stack, with the docs and gates that make them hold.
Every template carries the same fixed practices, stated in
[CONSTITUTION.md](CONSTITUTION.md):

- test-first, with the source code and its tests as the specification;
- 100% branch coverage from day one, honestly (visible exclusions, mutation testing);
- observability from day one: one canonical event per unit of work, a logger the linter enforces, a typed analytics catalogue, the platform's vitals;
- feature-first modules with enforced boundaries, constructor injection, unidirectional flow in UI stacks;
- one check command that CI runs unchanged.

Built from a research corpus of 623 sources (agent files in the wild, vendor
docs, papers, practitioner posts); the decisions and their evidence are in
[docs/specs/2026-09-08-template-collection.md](docs/specs/2026-09-08-template-collection.md)
and [core/evidence.md](core/evidence.md).

## Pick a stack

| Stack | Folder |
|---|---|
| Kotlin / Android (KMP notes included) | [stacks/kotlin-android](stacks/kotlin-android) |
| Swift / iOS | [stacks/swift-ios](stacks/swift-ios) |
| Dart / Flutter | [stacks/dart-flutter](stacks/dart-flutter) |
| Go | [stacks/go](stacks/go) |
| Rust | [stacks/rust](stacks/rust) |
| TypeScript / web (React + Node) | [stacks/typescript-web](stacks/typescript-web) |
| Python (FastAPI) | [stacks/python](stacks/python) |
| Java or Kotlin / Spring Boot | [stacks/java-spring](stacks/java-spring) |
| C# / .NET | [stacks/csharp-dotnet](stacks/csharp-dotnet) |

Each folder holds `AGENTS.md` (the always-loaded root, 100-150 lines),
`CLAUDE.md` (`@AGENTS.md`), `.github/copilot-instructions.md` (a pointer),
`agent_docs/{architecture,testing,observability,gates}.md` (read on demand),
and a `README.md` with the adoption steps.

## How to adopt

1. Copy the stack folder's files into your repository root.
2. Replace the placeholders and the exemplar paths with real files.
3. Ship every gate the root file names. A rule without its gate is deleted,
   not left as advice.
4. Delete what does not apply. Keep the root under 150 lines.
5. Run `python3 tools/check_templates.py` from this repo against your copy.

## Why the shape

The root file is short and every line names a command, a path, a tool or a
number, because the controlled evidence says context files barely move
correctness while exact commands, negative constraints and version-pinned
knowledge do. Style lives in the linter. Detail lives in `agent_docs/`. The
fixed practices are enforced by hooks, thresholds and architecture tests, not
by prose, because written instructions for logging or testing are followed a
third of the time. See [core/writing-agent-files.md](core/writing-agent-files.md).

## Layout

```
CONSTITUTION.md            the seven articles every template carries
core/                      writing-agent-files, practices/, architecture/, evidence.md
stacks/<stack>/            the templates
tools/check_templates.py   the validator (budgets, sections, directive rule, no platitudes, no style rules)
docs/specs/                design decisions
```

## Status

v0, 2026-09-08. Unmeasured: the templates have not yet been evaluated against
a no-template baseline on real tasks, which the evidence says is the only way
to know they help. That evaluation is the next piece of work.

Licence: Apache-2.0.
