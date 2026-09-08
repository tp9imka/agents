# kotlin-android template

Copy `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` and
`agent_docs/` into the repository root, then:

1. Replace `<Project>`, `<2.x>` and the `com.acme` package prefix.
2. Replace the exemplar paths under "Where to look" with two or three real
   files that show the patterns you want copied, and name any legacy module.
3. Ship the gates the file names: the Kover convention plugin, the Konsist
   `ArchitectureTest`, the detekt config with `ForbiddenMethodCall` and the
   analytics rule, the Roborazzi tasks, `apiCheck`, `lefthook.yml`, and the
   `check.yml` / `nightly.yml` workflows. A rule without its gate is deleted
   from `AGENTS.md`, not left as advice.
4. Add `core/observability` and `core/analytics` with `CanonicalEvent`,
   `Logger`, `AnalyticsEvent` and `OtelSetup` before the first feature.
5. Delete what does not apply. A template kept whole is a template nobody read.
6. Run `python3 tools/check_templates.py` from the collection against your
   copy before committing it; keep the root under 150 lines.

KMP or Compose Multiplatform: keep the file; swap Hilt for Koin with the
compiler plugin, Roborazzi for the platform's screenshot tool, and add the
`commonMain` / `androidMain` / `iosMain` layout to `agent_docs/architecture.md`.
