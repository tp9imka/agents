# typescript-web template

Copy `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` and
`agent_docs/` into the repository root, then:

1. Replace `<Project>`, the versions, the framework choices (Vite/Next, Fastify/NestJS) and the exemplar paths with real files.
2. Ship the gates the file names: root `package.json` scripts, `biome.json`,
   `tsconfig.base.json` strict options, `.dependency-cruiser.cjs`,
   `vitest.config.ts` thresholds, `stryker.config.mjs`, `lefthook.yml`, the
   `check.yml` / `nightly.yml` workflows, tdd-guard in `.claude/settings.json`.
3. Add `packages/core/observability` and `packages/core/analytics` before the first feature.
4. For a NestJS server, keep the rules and map DI to providers with `Symbol` tokens for interfaces.
5. Delete what does not apply; keep the root under 150 lines and run the
   collection's `tools/check_templates.py` against your copy.
