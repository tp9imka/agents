# java-spring template

For Java or Kotlin services on Spring Boot. Copy `AGENTS.md`, `CLAUDE.md`,
`.github/copilot-instructions.md` and `agent_docs/` into the repository root, then:

1. Replace `<Project>`, the versions, `com.acme` and the exemplar paths with real files.
2. Ship the gates the file names: `build.gradle.kts` with `check` wired to
   JaCoCo (or Kover) verification, `ArchitectureTest` and `ModularityTest`,
   Spotless, Checkstyle (or detekt), `logback-spring.xml` with masking,
   `lefthook.yml`, the `check.yml` / `nightly.yml` workflows.
3. Add `com.acme.observability` and `com.acme.analytics` before the first module.
4. For Kotlin, apply the "Kotlin variant" notes in `agent_docs/architecture.md`
   and swap the tool names in `AGENTS.md`.
5. Delete what does not apply (messaging, jOOQ); keep the root under 150
   lines and run the collection's `tools/check_templates.py` against your copy.
