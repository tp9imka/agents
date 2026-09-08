# Writing agent files

How every `AGENTS.md` in this collection is written, and why. Evidence for each
rule is in [evidence.md](evidence.md).

## The budget

- Root file: 100-150 lines. Hard stop at 200. `tools/check_templates.py` fails above it.
- The loaded chain (root plus nested files an agent reads) stays under 32 KiB;
  Codex truncates there. Windsurf caps 6,000 characters per file.
- At most 12 links out of the root. Linked references are read in over 90% of
  sessions; unlinked docs in under 10%.
- Every line is loaded into every session. A line that applies only sometimes
  costs every session and belongs in `agent_docs/` or a skill.

## The anatomy

In this order. Commands are the highest-value section; put them first.

1. One paragraph: what the project is and the stack with versions.
2. Commands: setup, build, test all, test one file, lint and format, the single
   check command. Include real flags. Say which command to prefer while iterating.
3. Architecture invariants: the module rule, the layer direction, the DI rule,
   each with the gate that checks it.
4. Testing: the TDD rule, the definition of done, the coverage gate, where tests live.
5. Observability: the canonical event, the logger, the analytics catalogue,
   the vitals, the privacy rule, each with its enforcer.
6. Boundaries: Always / Ask first / Never. Every Never points at the alternative.
7. Where to look: `agent_docs/` files with one line each, exemplar files by path.
8. Maintenance: how rules are added and removed.

## The directive rule

A directive names a path, a command, a tool, a file or a number. "Write clean
code", "follow best practices", "be careful with concurrency" are deleted.
Compare:

- Weak: "Run tests before committing."
- Strong: "Before committing run `make check`; it is the CI gate."

Negative constraints are the lines that measurably help. Keep them few and
pair each with the concrete alternative: "Never call the database from a
handler; go through the port in `internal/<feature>/ports.go`."

## What stays out

- Style and formatting rules. The linter and formatter config ships instead.
- Codebase tours and directory listings. Agents find files as fast without them.
- Anything an agent can read from `package.json`, `go.mod`, `pubspec.yaml` or the CI file.
- Information that changes weekly: milestones, inventories, current status.
- Personas ("you are a senior engineer"). Role prose does not change behaviour.
- Patterns the codebase does not yet follow. Agents implement aspirational
  patterns immediately and inconsistently.

## Tool shims

`AGENTS.md` is canonical. Other tools point at it:

| Tool | File | Content |
|---|---|---|
| Claude Code | `CLAUDE.md` | `@AGENTS.md` |
| Codex | none | reads `AGENTS.md` natively, root down, closer wins, 32 KiB cap |
| Gemini CLI | `.gemini/settings.json` | `"context": { "fileName": ["AGENTS.md"] }` |
| Copilot | `.github/copilot-instructions.md` | "Follow `AGENTS.md`." |
| Cursor | none | reads `AGENTS.md`; optional `.cursor/rules/*.mdc` mirrors of `agent_docs/` |
| Amp, OpenCode, Zed, Kiro, Junie | none | read `AGENTS.md` natively |

Nested `AGENTS.md` files in packages hold package-specific commands only; the
root holds cross-cutting rules; nothing is duplicated.

## Enforcement beats prose

An instruction is advisory; a hook, a linter or a test is not. For each of the
fixed practices the template ships the enforcer:

| Practice | Enforcer |
|---|---|
| Test-first | TDD hook where the stack has one; diff rule "tests fail without the change" in review |
| Coverage | threshold in the check command; mutation run in CI |
| Observability | lint rule against raw logging; a test asserting the canonical event |
| Architecture | layer gate in the check command |
| Style | formatter and linter, auto-fixed by a hook |

## The maintenance loop

1. Add a line only after an observed failure. Then revert, re-run the task with
   the line in place, and keep it only if the outcome changed.
2. Every rule carries its enforcer or its reason, so it can be deleted safely later.
3. Revisit after each model release. Rules that worked around an old limitation
   become overhead.
4. When a command is complex enough to need a paragraph, write a script with a
   plain interface and document the script.
5. Rewrite whole, do not append. A file edited by appending stops being read.

## Acceptance

A template is accepted when `tools/check_templates.py` passes and a project
generated from it passes its own check command on the first run.
