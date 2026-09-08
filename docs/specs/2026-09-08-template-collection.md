# Template collection - design spec

Date: 2026-09-08. Status: v0, built from the phase-1 research corpus
(`Projects/agents/research/` in the knowledge vault, 623 sources, 257 assessed).
Record slugs in this document refer to that corpus; the public URL is in each record.

## 1. What this repo is

A collection of `AGENTS.md` templates and the supporting docs, organised by
**stack**, not by platform, that carry a fixed set of house practices:

- TDD, with the source code and its tests as the specification. No spec for the spec.
- Observability from day one: structured logs, usage statistics, performance traces.
- 100% coverage from day one, enforced.

Plus architecture guidance per stack: clean / hexagonal dependency rule inside
feature-first modules, dependency injection, unidirectional flow for UI stacks.

Stacks in v0: `kotlin-android`, `swift-ios`, `dart-flutter`, `go`, `rust`,
`typescript-web`, `python`, `java-spring` (Java and Kotlin server), `csharp-dotnet`.
Out of scope for v0: C++, desktop shells, KMP as a separate stack (folded into
`kotlin-android` notes).

## 2. Decisions taken from the evidence

Each decision names the records it rests on. Where sources disagree, the
resolution is stated.

**D1. Root file is short, mechanical, and every line names something checkable.**
Controlled studies found context files barely move correctness
(`eth-evaluating-agents-md`, `khatri-do-context-files-help`); what agents reliably
follow is exact commands and tools (used 160x more when named), version-pinned
knowledge the model lacks (`vercel-agents-md-outperforms-skills`), and negative
constraints (`zhang-guardrails-beat-guidance`). 73% of a typical file is
scaffolding and 90% of directives name nothing concrete
(`reporails-state-of-ai-instruction-quality`). Rule: a directive must name a path,
command, tool or file; otherwise it is deleted or moved to a linter.

**D2. Budget: 100-150 lines target, 200 hard; whole chain under 32 KiB; at most
12 links.** `augmentcode-good-agents-md-files` (gains reverse past ~300 lines),
`people/humanlayer` (150-200 instruction budget, ~50 used by the harness),
Codex truncation at 32 KiB (`openai-codex-agents-md-docs`), Windsurf 6,000 chars
per file. Enforced by `tools/check_templates.py`.

**D3. Anatomy.** Commands first (setup, build, test all, test one, lint and
format, the single check command), then architecture invariants, testing rules
with the definition of done, observability rules, boundaries as Always / Ask
first / Never, then links. From `taiizor-agents-md-cookbook`,
`github-blog-agents-md-2500-repos`, `agentsmd-agents-md`, and the exemplar
files (`android-nowinandroid`, `cloudflare-workers-sdk`, `apache-airflow`,
`evrone-go-clean-template`, `colinhacks-zod`).

**D4. Style rules do not live in the file.** Linter and formatter config ships
with the template instead (`vendors/cursor-docs-rules`, `people/humanlayer`,
`dos-santos-configuration-smells-agents-md` - lint leakage in 62% of files).

**D5. Every rule names its enforcer, or its reason.** Rules without one accrete
forever (`chakrabarti-why-claude-md-keeps-growing`, house baseline
`writing-agent-docs`). Format: `Rule. Enforced by <gate>.` or `Rule. Because <reason>.`

**D6. Progressive disclosure through `agent_docs/`.** Stack detail lives in
`agent_docs/{architecture,testing,observability,gates}.md`, listed in the root
with one-line descriptions. Linked references are read in over 90% of sessions;
orphan docs under 10% (`augmentcode-good-agents-md-files`). Exception per
`vercel-agents-md-outperforms-skills`: version-pinned API corrections the model
gets wrong stay in the always-loaded root, compressed.

**D7. Tool shims are pointers, not copies.** `AGENTS.md` is canonical.
`CLAUDE.md` contains `@AGENTS.md` (`getsentry-sentry`,
`claude-code-docs-memory`). Codex reads it natively. Gemini via
`context.fileName` (`google-gemini-cli-gemini-md`). Copilot via a one-line
`.github/copilot-instructions.md`. Cursor reads `AGENTS.md`; path-scoped
`.cursor/rules/*.mdc` are optional mirrors of `agent_docs/`.

**D8. TDD is test-first with a design step and a fail-without-change check,
enforced by a hook where one exists.** Wording from `kent-beck-augmented-coding`
and `obra-superpowers` (Iron Law); enforcer `nizos-tdd-guard` / Probity where the
stack has a reporter; the diff rule from `apache-airflow` ("every test must fail
without the PR's change"). Strict in-loop micro red-green is not mandated:
`martinfowler-tdd-in-the-agent-loop` found it no better than test-first with an
up-front design at 3x tokens, and `danluu-agentic-testing` measured testing
instructions head to head. Resolution: plan the shape, list the tests, then
red-green per test.

**D9. The source is the spec.** Vocabulary from `boeckeler-sdd-3-tools`: the
project is spec-first (a plan of tests precedes code) but the anchored artifact
is the code and its tests, never a requirements or design document. Anchors:
`gojko-specification-by-example`, `lexi-lambda-parse-dont-validate` (types as
spec), Rust doctests, `duckdb-duckdb` (sqllogictest), `gotalab-cc-sdd` ("Code
remains the source of truth"). Kept from spec-kit: a short versioned
`CONSTITUTION.md` and dependency-annotated task lists. Dropped: requirements.md,
design.md, PRDs. ADRs are allowed for decisions, not for features.

**D10. 100% coverage means branch coverage, visible exclusions, and mutation
testing.** Pro: `vgv-road-to-100-test-coverage`, `sqlite-testing`. Counter:
`martin-fowler-test-coverage`, `codecov-case-against-100-coverage`,
`ploeh-100-coverage-is-not-that-trivial`. Data: agents left alone test half
their changes and skip error paths (`dipongkor-test-coverage-agentic-prs`).
Rules: threshold 100 in the check command (branch where the tool supports it);
exclusions only by in-code marker with a reason, never by config; a mutation run
(`cargo-mutants`, Stryker, PIT, mutmut) on the core packages in CI; tests are
part of "done". The house baseline's ratchet applies when adopting an existing
repo; greenfield starts at 100.

**D11. Observability is structural, not prose.** Written logging instructions
fail two thirds of the time (`ouatiti-do-agents-log-like-humans`). Per stack the
template ships: one canonical event per unit of work emitted in a finally block
(`stripe-canonical-log-lines`, `jeremy-morrell-wide-events`), OTel attribute
names (`otel-semantic-conventions`), a logger the linter forbids bypassing
(`cloudflare-workers-sdk`), a test that asserts the event was emitted
(`apache-airflow`), privacy rules for mobile (`element-hq-element-x-ios`,
`android-log-info-disclosure`, `apple-oslog-generating-log-messages`), platform
performance metrics (`sentry-mobile-vitals`, `web-dev-custom-metrics`, four
golden signals from `google-sre-monitoring-distributed-systems`), and a typed
analytics event catalogue (`segment-tracking-plan-best-practices`). Level policy:
debug for developers, info for operators, error for handled failures; a warning
must be actionable (`dave-cheney-lets-talk-about-logging`).

**D12. Architecture: feature-first modules with enforced boundaries, dependency
rule inside.** `uncle-bob-clean-architecture`, `cockburn-hexagonal-architecture`,
`herbertograca-explicit-architecture`, `sairyss-domain-driven-hexagon` for the
rule and vocabulary; `vgv-engineering` (FFCA), `thunderbird-thunderbird-android`
(api/internal split), `android-modularization-guide`, `feature-sliced-design`,
`bogard-vertical-slice-architecture` for feature-first. Resolution: hexagonal
ports at module boundaries, vertical slices within, both enforced by a layer
gate per stack (`lemonappdev-konsist`, `tng-archunit-examples`,
`sverweij-dependency-cruiser`, `seddonym-import-linter`, `fe3dback-go-arch-lint`,
cargo-modules, Swift package targets, Dart packages).

**D13. DI: constructor injection, composition root, compile-time graph where the
stack has one.** `fowler-dependency-injection`,
`ploeh-service-locator-anti-pattern`; per stack Hilt or Koin (compile-safe) or
Metro, swift-dependencies or Factory, injectable over get_it, hand wiring or Fx,
NestJS providers, .NET built-in DI, python-dependency-injector optional.

**D14. UI stacks use unidirectional flow.** `redux-style-guide` rules transfer to
bloc, ViewModel+StateFlow, TCA or `@Observable`, with tests per state transition.

**D15. Maintenance loop is written into the template.** Add a line only after an
observed failure and re-run the task to confirm it helps
(`hn-evaluating-agents-md-thread`, `mitchell-hashimoto-ai-adoption-journey`);
prune after model releases and let a Stop hook propose updates
(`claude-code-docs-large-codebases`); fix the tool instead of documenting it
(`sshh-how-i-use-every-claude-code-feature`,
`armin-ronacher-agentic-coding-recommendations`).

**D16. Templates are validated, not assumed.** A template passes
`tools/check_templates.py` (budgets, required sections, directive concreteness,
no platitudes, no style rules) and its generated project passes its own gates
(`verygoodopensource-very-good-templates` acceptance pattern). The ETH conclusion
"any attempts to improve performance should be rigorously evaluated" is the
standing caveat: v0 is unmeasured.

## 3. Repository layout

```
agents/
  README.md                      how to pick a stack, copy, delete what does not apply
  AGENTS.md                      this repo's own agent file (dogfoods the core)
  CONSTITUTION.md                the fixed practices as a short versioned constitution
  docs/specs/                    this spec and later ones
  core/
    writing-agent-files.md       budget, anatomy, directive rule, anti-patterns, maintenance loop
    practices/
      tdd.md                     rule, definition of done, enforcers per stack
      source-is-the-spec.md      the SDD position and what replaces spec documents
      coverage.md                100% branch, exclusion policy, mutation, per-stack tools
      observability.md           canonical event, logger, analytics catalogue, vitals, privacy
      gates.md                   one check command, CI = local, layer gate, drift gate, hooks
    architecture/
      principles.md              dependency rule, ports and adapters vocabulary, feature-first
      dependency-injection.md
      modularization.md
      unidirectional-flow.md
    evidence.md                  the records behind every decision, with public URLs
  stacks/<stack>/
    AGENTS.md                    the template (target 100-150 lines)
    CLAUDE.md                    @AGENTS.md
    .github/copilot-instructions.md   one-line pointer
    agent_docs/architecture.md  layout, module rule, DI, the gate config
    agent_docs/testing.md       runner, TDD workflow, coverage gate config, mutation, golden tests
    agent_docs/observability.md canonical event, logger setup, analytics catalogue, vitals, privacy
    agent_docs/gates.md         the check command, CI workflow, hooks
    README.md                    what to change when adopting
  tools/
    check_templates.py           the validator; run in CI
  .github/workflows/check.yml    runs the validator on every push
```

## 4. Build order

1. Core docs and the constitution (this commit set).
2. Validator.
3. Stacks in this order: kotlin-android, swift-ios, dart-flutter, go, rust,
   typescript-web, python, java-spring, csharp-dotnet.
4. Repo README and the repo's own AGENTS.md.

## 5. Open questions for Ivan

- Whether the Kotlin server template should be `java-spring` (shared) or split.
- Whether to ship `.cursor/rules/*.mdc` mirrors in v0 or only `agent_docs/`.
- Attribution policy default (co-author trailers on or off); the corpus has both.
- Whether to keep the 100% line for adoption into existing repos or use the
  house ratchet there.
