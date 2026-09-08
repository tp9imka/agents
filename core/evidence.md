# Evidence

The decisions in `docs/specs/2026-09-08-template-collection.md` and the rules
in `core/` rest on these sources. Slugs are records in the research corpus
(`Projects/agents/research/` in the knowledge vault, ledger `_Index.md`), which
hold the quoted passages with file and line. Public URLs where the source is
public; papers by arXiv id where known, otherwise "arXiv, see record".

## D1 - short, mechanical, checkable lines

- `eth-evaluating-agents-md` - Gloaguen et al., Evaluating AGENTS.md, arXiv 2602.11988
- `khatri-do-context-files-help` - controlled ablation, 288 runs, arXiv (see record)
- `zhang-guardrails-beat-guidance` - 679 rule files, 5,000 runs; negative constraints help, arXiv (see record)
- `vercel-agents-md-outperforms-skills` - vercel.com/blog, AGENTS.md index beat skills 100% vs 79%
- `reporails-state-of-ai-instruction-quality` - reporails.dev, 28k projects; 73% scaffolding
- `people/philipp-schmid` - philschmid.de/writing-good-agents
- `people/humanlayer` - humanlayer.dev/blog/writing-a-good-claude-md
- `lulla-agents-md-efficiency` - runtime -28%, tokens -17% with a file, arXiv (see record)

## D2 - budget

- `augmentcode-good-agents-md-files` - augmentcode.com blog; 100-150 lines, discovery rates
- `people/humanlayer` - 150-200 instruction budget
- `openai-codex-agents-md-docs` - developers.openai.com/codex; 32 KiB `project_doc_max_bytes`
- `collections/taiizor-agents-md-cookbook` - github.com/Taiizor/agents-md-cookbook; Windsurf caps
- `mcmillan-instruction-adherence-factorial` - 1,650 sessions factorial study, arXiv (see record)

## D3 - anatomy

- `collections/taiizor-agents-md-cookbook` - anatomy, best practices, linter
- `github-blog-agents-md-2500-repos` - github.blog; Always / Ask first / Never
- `collections/agentsmd-agents-md` and `agents-md-spec` - agents.md
- `repos/kotlin-android/android-nowinandroid` - github.com/android/nowinandroid/blob/main/AGENTS.md
- `repos/typescript-web/cloudflare-workers-sdk` - github.com/cloudflare/workers-sdk/blob/main/AGENTS.md
- `repos/python/apache-airflow` - github.com/apache/airflow/blob/main/AGENTS.md
- `repos/go/evrone-go-clean-template` - github.com/evrone/go-clean-template/blob/main/AGENTS.md
- `repos/typescript-web/colinhacks-zod` - github.com/colinhacks/zod/blob/main/AGENTS.md
- `repos/multi/getsentry-sentry` - github.com/getsentry/sentry/blob/master/AGENTS.md
- `people/builder-io-steve-sewell` - builder.io/blog/agents-md

## D4 - style out of the file

- `vendors/cursor-docs-rules` - cursor.com/docs/context/rules
- `dos-santos-configuration-smells-agents-md` - six smells, lint leakage 62%, arXiv (see record)
- `people/humanlayer` - "never send an LLM to do a linter's job"

## D5 - every rule names its enforcer or reason

- `chakrabarti-why-claude-md-keeps-growing` - +226% growth, comments halt it, arXiv (see record)
- `house-baseline` - `Projects/+General/common/agents/writing-agent-docs.md`
- `vendors/claude-code-docs-memory` - code.claude.com/docs/en/memory

## D6 - progressive disclosure

- `augmentcode-good-agents-md-files` - linked refs read >90%, orphans <10%
- `vendors/anthropic/anthropic-effective-context-engineering` - anthropic.com/engineering
- `people/martin-fowler-site/martinfowler-context-engineering-coding-agents` - martinfowler.com
- `collections/vercel-agents-md-outperforms-skills` - the exception for stale-API knowledge

## D7 - tool shims

- `repos/multi/getsentry-sentry` - `CLAUDE.md` = `@AGENTS.md`
- `vendors/claude-code-docs-memory`, `vendors/openai/openai-codex-agents-md-docs`,
  `vendors/google/google-gemini-cli-gemini-md` (geminicli.com), `vendors/github-copilot-docs-repository-instructions` (docs.github.com),
  `vendors/kiro-docs-steering` (kiro.dev/docs/steering), `vendors/amp/amp-agents-md-docs` (ampcode.com)

## D8 - TDD

- `practices/tdd/kent-beck-augmented-coding` - tidyfirst.substack.com, "Augmented Coding: Beyond the Vibes" with the system prompt
- `collections/obra-superpowers` - github.com/obra/superpowers, test-driven-development skill
- `practices/tdd/nizos-tdd-guard` - github.com/nizos/tdd-guard (successor: github.com/nizos/probity)
- `repos/python/apache-airflow` - "every test must fail without the PR's change"
- `people/martin-fowler-site/martinfowler-tdd-in-the-agent-loop` - martinfowler.com, no measurable gain, 3x tokens
- `community/blogs/danluu-agentic-testing` - danluu.com, 26 testing conditions
- `dipongkor-test-coverage-agentic-prs` - agents test 49.6% of changes, arXiv (see record)
- `mathews-tdd-for-code-generation` - tests in the prompt raise pass rates, arXiv (see record)
- `practices/tdd/fowler-practical-test-pyramid` - martinfowler.com/articles/practical-test-pyramid.html
- `practices/tdd/kent-beck-test-desiderata` - kentbeck.github.io/TestDesiderata

## D9 - source is the spec

- `practices/sdd/boeckeler-sdd-3-tools` - martinfowler.com, spec-first / anchored / as-source
- `practices/sdd/gojko-specification-by-example` - gojko.net
- `practices/sdd/lexi-lambda-parse-dont-validate` - lexi-lambda.github.io
- `repos/cpp/duckdb-duckdb` - sqllogictest as executable spec
- `practices/sdd/gotalab-cc-sdd` - "Code remains the source of truth"
- `collections/github-spec-kit` - github.com/github/spec-kit (constitution kept, document stack dropped)
- `practices/sdd/zaninotto-sdd-waterfall-strikes-back` - marmelab.com
- `vendors/claude-new-rules-context-engineering-claude5` - "prefer files that are in code"

## D10 - coverage

- `practices/coverage/vgv-road-to-100-test-coverage` - verygood.ventures blog
- `practices/coverage/sqlite-testing` - sqlite.org/testing.html
- `practices/coverage/martin-fowler-test-coverage` - martinfowler.com/bliki/TestCoverage.html
- `practices/coverage/codecov-case-against-100-coverage` - about.codecov.io
- `practices/coverage/ploeh-100-coverage-is-not-that-trivial` - blog.ploeh.dk
- `practices/coverage/sourcefrog-cargo-mutants` - github.com/sourcefrog/cargo-mutants
- `practices/tdd/testdouble-mutation-testing-agents` - testdouble.com
- `practices/coverage/coveragepy-excluding-code`, `taiki-e-cargo-llvm-cov`, `vitest-coverage-config`, `coverlet-coverage-coverlet`, `vladopajic-go-test-coverage`, `verygoodopensource-very-good-workflows`

## D11 - observability

- `practices/observability/stripe-canonical-log-lines` - stripe.com/blog/canonical-log-lines
- `practices/observability/jeremy-morrell-wide-events` - jeremymorrell.dev
- `practices/observability/boris-tane-wide-events-101` - boristane.com
- `practices/observability/otel-semantic-conventions` - github.com/open-telemetry/semantic-conventions
- `practices/observability/otel-specification-logs-data-model` - opentelemetry.io/docs/specs/otel/logs/data-model
- `practices/observability/w3c-trace-context` - w3.org/TR/trace-context
- `practices/observability/google-sre-monitoring-distributed-systems` - sre.google/sre-book
- `practices/observability/dave-cheney-lets-talk-about-logging` - dave.cheney.net
- `practices/observability/sentry-mobile-vitals` - docs.sentry.io
- `practices/observability/web-dev-custom-metrics` - web.dev/articles/custom-metrics
- `practices/observability/segment-tracking-plan-best-practices`, `firebase-analytics-event-naming-rules`, `posthog-product-analytics-best-practices`
- `practices/observability/apple-oslog-generating-log-messages` - developer.apple.com/documentation/os
- `practices/observability/android-log-info-disclosure` - developer.android.com/privacy-and-security
- `repos/swift-ios/element-hq-element-x-ios` - PII and logging rules
- `repos/typescript-web/cloudflare-workers-sdk` - logger rule
- `ouatiti-do-agents-log-like-humans` - 4,550 agentic PRs, arXiv (see record)

## D12 - architecture

- `architecture/clean/uncle-bob-clean-architecture` - blog.cleancoder.com
- `architecture/hexagonal/cockburn-hexagonal-architecture` - alistair.cockburn.us
- `architecture/hexagonal/herbertograca-explicit-architecture` - herbertograca.com
- `architecture/hexagonal/sairyss-domain-driven-hexagon` - github.com/Sairyss/domain-driven-hexagon
- `architecture/clean/vgv-engineering` - Feature-First Clean Architecture
- `repos/kotlin-android/thunderbird-thunderbird-android` - api/internal split, ADR-0009
- `architecture/modularization/android-modularization-guide` - developer.android.com/topic/modularization
- `architecture/modularization/feature-sliced-design` - feature-sliced.design
- `architecture/modularization/bogard-vertical-slice-architecture` - jimmybogard.com
- `people/armin-ronacher/armin-ronacher-agentic-coding-recommendations` - lucumr.pocoo.org
- `repos/rust/openai-codex` - module size rule
- gates: `lemonappdev-konsist`, `tng-archunit-examples`, `sverweij-dependency-cruiser`, `seddonym-import-linter`, `fe3dback-go-arch-lint`, `regexident-cargo-modules`
- `larsen-architectural-quality-agentic-ai` - adoption alone does not improve architecture, arXiv (see record)

## D13 - dependency injection

- `architecture/dependency-injection/fowler-dependency-injection` - martinfowler.com/articles/injection.html
- `architecture/dependency-injection/ploeh-service-locator-anti-pattern` - blog.ploeh.dk
- `android-dependency-injection-guide`, `insertkoinio-koin`, `google-dagger`, `zacsweers-metro`, `pointfreeco-swift-dependencies`, `milad-akarie-injectable`, `flutter-it-get_it`, `uber-go-fx`, `google-wire`, `nestjs-custom-providers`, `ets-labs-python-dependency-injector`

## D14 - unidirectional flow

- `architecture/unidirectional-flow/redux-style-guide` - redux.js.org/style-guide
- `felangel-bloc`, `pointfreeco-swift-composable-architecture`, `orbit-mvi-orbit-mvi`, `android-architecture-guide`

## D15 - maintenance loop

- `research-papers/hn-evaluating-agents-md-thread` - news.ycombinator.com/item?id=47034087
- `people/mitchell-hashimoto/mitchell-hashimoto-ai-adoption-journey` - mitchellh.com
- `people/fabien-sanglard/fabien-sanglard-agent-md` - fabiensanglard.net
- `vendors/claude-code-docs-large-codebases` - code.claude.com/docs/en/large-codebases
- `community/blogs/sshh-how-i-use-every-claude-code-feature` - blog.sshh.io

## D16 - validation

- `repos/dart-flutter/verygoodopensource-very-good-templates` - generate, then run the output's own gates
- `research-papers/eth-evaluating-agents-md` - "rigorously evaluated before deployment"
- `research-papers/metr-early-2025-ai-developer-productivity` - the perception gap, arXiv (see record)
