# Constitution

Version 0.1.0 | Ratified 2026-09-08 | Last amended 2026-09-08

Applies to every project generated from this collection. A stack template or an
`agent_docs/` page may add rules; it may not contradict these. Amend by editing
this file, bumping the version, and stating the reason in the commit message.

## I. The source is the specification

- A change is specified by the tests and types written for it, before the
  implementation. No requirements or design documents are kept for features.
- Architectural decisions get a short ADR under `docs/adr/`. Nothing else is a spec.
- When asked for a spec, produce a checklist of tests and a task list, not prose.

## II. Test-first (non-negotiable)

- No production code without a test that fails first and passes after. A change
  whose tests pass with the change stashed is not done.
- Plan the shape before the first test: name the modules and types the change
  touches, then list the tests, then work the list red => green => refactor.
- Never disable, delete or weaken a test to get green. Ask instead.

## III. 100% coverage, honestly

- The check command fails below 100% branch coverage (line where the tool
  cannot measure branches). Exclusions exist only as in-code markers with a
  reason, never as configuration.
- A mutation run on the core packages is part of CI. Coverage measures the test
  suite; the mutation score measures whether the tests check anything.

## IV. Observability from day one

- Every unit of work (request, job, screen, command) emits one structured
  canonical event with ids, outcome, duration and the business fields, in a
  finally block. Nothing writes to stdout or the platform log except the logger.
- Usage events come from a typed catalogue. Performance metrics are the
  platform's vitals, emitted from the first build.
- No secrets, credentials or personal data in logs or events.

## V. Enforced architecture

- Feature-first modules with hexagonal ports at their boundaries; inside, the
  dependency rule: source dependencies point inward, adapters depend on the core.
- Every module boundary and layer direction is checked by a gate in the check
  command. A rule without a gate is documentation.
- Dependencies are injected through constructors and wired once at the
  composition root.

## VI. One command, the same everywhere

- One command runs format, lint, layer gate, tests with coverage, and drift
  checks for generated code. CI runs that command and nothing else.
- Local hooks run the fast subset before commit.

## VII. Simplicity

- Do the simplest thing that satisfies the tests. No abstraction for a single
  use. No feature beyond the request. Delete the old path when replacing it.

## Governance

- The `AGENTS.md` of a project states these seven articles in one line each and
  names the gate that enforces each. Review verifies the gates run, not the prose.
- Complexity must be justified in the change description. Amendments to this
  constitution require a version bump.
