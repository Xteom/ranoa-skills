# v6 design exchange — round 2 (Experiment 1 results -> Codex critique)

Date: 2026-08-13. Round 1 produced the charter (`2026-08-13-v6-coverage-denominator-charter.md`).
Round 2: we ran the first shadow-mode denominator prototype against pi and deer-flow
(ground truth = the blind audits' silent-omission lists) and sent the results to Codex.

## Experiment 1 results (summary)

- FS denominator FAILED structurally: bucketing collapsed (5 buckets on pi, 2 on deer-flow; real gaps live 3 levels deep, e.g. packages/coding-agent/src/utils/), and the generous basename word-match marked everything rowed -> zero fs-axis recall.
- Risk denominator WORKED with noise: flagged unrowed version-check.ts + windows-self-update.ts (= self-update finding), http-dispatcher.ts + node-http-proxy.ts (= net chokepoint), telemetry.ts + provider-attribution.ts (= analytics) — but drowned in per-file test/migration noise, plus one substring bug: "regression" contains "egress".
- Reconciliation needs the inward pass's normalization arsenal (credential-store.ts vs "credential stores"; update_agent_tool.py vs update_agent).
- Inside-file findings (glob/grep, skill_manage, RuntimeFeatures) are invisible to any file-level denominator by construction — separate closed-enumeration mechanism confirmed.

## The prompt sent to Codex

```text
Round 2 of our design exchange on the coverage-denominator mechanism ("v6") for the repo-expert-onboarding skill. You previously reviewed the roadmap and set the contract (gate exact-path inventory reconciliation, not discovery; filesystem + risk denominators; schema; shadow-mode calibration). We ran the first shadow-mode experiment. Here are the results — critique the mechanism and answer the design questions at the end. You are in the skill's repo (branch main); charter at `docs/2026-08-13-v6-coverage-denominator-charter.md`.

## Experiment 1 setup

Prototype (pure Python, no LLM): two denominators over a repo, reconciled against guide text in shadow mode.
- FS denominator: package roots via manifest detection (package.json/pyproject/...), buckets = immediate subdirs of each package's src/, plus repo-root top-level dirs not in packages.
- Risk denominator: regex patterns over file paths for {workflows, deploy manifests, migrations, auth/secret/token/oauth-named files, update/install/version-check-named files, route registries, proxy/dispatcher/egress-named files, telemetry/analytics/tracking-named}.
- Reconciliation proxy (shadow): item counts as "rowed" if its relpath appears in the guide text OR its basename matches with word boundaries. (Deliberately generous.)

Ground truth: two guides whose silent omissions are known from 4 independent blind audits (pi: image-ingestion pipeline in src/utils/, http-dispatcher, model-resolver, analytics plane, session-analysis scripts, self-update path; deer-flow: scripts/wizard/, frontend i18n, Next /api/memory route handlers, deerflow/utils/, glob+grep tools inside sandbox/tools.py, skill_manage tool, RuntimeFeatures assembly path).

## Results

FS denominator: FAILED structurally. Produced only 5 buckets on pi (a 5-package TS monorepo, ~100k LOC) and 2 on deer-flow (uv+pnpm monorepo). Zero unrowed buckets -> zero recall on the fs axis. Two causes: (a) bucketing algorithm collapsed (package/container overlap logic wrong; depth insufficient — pi's real gap lives at packages/coding-agent/src/utils/, three levels deep); (b) the generous basename word-match made everything "rowed" (e.g. bucket "utils" matches the word "utils" anywhere in 300KB of guide text).

Risk denominator: WORKED with noise. On pi it flagged, unrowed: version-check.ts, windows-self-update.ts (= the audits' self-update finding), http-dispatcher.ts + node-http-proxy.ts (= the net-chokepoint finding), telemetry.ts + provider-attribution.ts (= the analytics finding), credential-store.ts (FALSE positive — guide covers "credential stores" as prose; basename token match failed on hyphen/plural), oauth-selector.ts, plus ~20 test files. On deer-flow: Dockerfile, mcp/oauth.py, skills/installer.py, update_agent_tool.py (FP — the guide enumerates update_agent; name normalization failed), individual migration files (should be one dir-level item), ~25 test files.

Noise taxonomy: (1) test files dominate both lists — guides cover tests as a family, not per-file; (2) migration FILES flagged individually where the migrations DIRECTORY is the honest unit; (3) substring bug: "regression" contains "egress", so tui regression tests matched the egress pattern — need token-boundary-safe patterns; (4) reconciliation needs the same normalization arsenal our inward pass uses (camel/kebab/snake splitting, light stemming, separator-stripped compare) instead of bare word-boundary basename.

Notably: the audits' INSIDE-a-covered-file findings (glob/grep tools inside sandbox/tools.py; skill_manage inside tools.py; RuntimeFeatures inside factory.py) are invisible to BOTH denominators by construction — file-level walking cannot see registry entries. That matches your earlier point that closed-enumeration checking is a separate mechanism.

## Design questions

1. FS bucketing: propose a concrete algorithm that would have produced the right buckets on these two repos (pi: packages/{ai,agent,coding-agent,tui,orchestrator}/src/* subdirs incl. utils/, cli/, core/ children; deer-flow: backend/packages/harness/deerflow/* subpackages, frontend/src/core/* + components/* + app/*, scripts/*). Recurse-until-what? Manifest-only roots miss src-internal structure; unlimited recursion produces hundreds of buckets. Is "recurse while a dir exceeds N LOC AND has >=2 code-bearing children" sane, or do you have a better ownership-boundary rule?
2. Reconciliation matching for shadow mode AND for the eventual gate: the gate contract says exact paths/globs in a schema'd inventory — fine. But MIGRATING existing guides needs a matcher against prose. Would you accept: path-suffix match OR separator-stripped stemmed containment, with anything weaker counting as unrowed? Where would you set the bar to keep gate-precision?
3. Risk denominator refinements: (a) exclude test trees entirely or map them to a single "tests" family item? (b) dir-level units for migrations/workflows — what other families deserve dir-level rollup? (c) our pattern list vs your "semantic/risk" list — what's missing that the known findings imply? (d) how do we keep name-based risk patterns from being gamed or from missing unnamed risks (e.g. model-resolver.ts carries no risk-looking name — should risk detection also key on imports/APIs like child_process, fetch override, fs chmod, env access?)
4. The schema: for the machine-readable inventory, do you prefer (a) a sidecar YAML/JSON file in the guide dir that the appendix table is rendered from, or (b) a strictly-formatted markdown table the validator parses? Argue trade-offs briefly — authorship is by LLM agents, consumers are the validator + human readers.
5. Experiment 2 design: what should we measure next, on which repos, before writing the v6 spec? Be concrete.

Dense numbered answers. Disagree where warranted.
```

## Codex verdict (verbatim)

The experiment supports the charter’s core separation, but “risk denominator worked” is slightly too strong. It proved useful; it did not yet establish acceptable recall. More importantly, discovery quality and prose-reconciliation quality were conflated. Experiment 2 should score them independently.

1. **FS bucketing: use a deterministic coverage frontier, not recursive LOC bucketing alone.**

   “Ownership boundary” is too strong for what a filesystem can infer. Use an evidence hierarchy:

   1. Explicit configuration: `force_split`, `force_leaf`, ignored/generated families.
   2. Strong boundaries: workspace members, nested manifests/build targets, package exports, CODEOWNERS changes.
   3. Conventional code roots: `src/`, Python import packages, `app/`, `lib/`, plus operational roots such as `scripts/`, `tools/`, `infra/`, and hidden extension roots.
   4. Adaptive size/shape splitting as the fallback.

   Concrete frontier algorithm:

   - Discover workspace/package roots.
   - Inside each package, discover source anchors from build configuration first and conventions second. For deer-flow, `backend/packages/harness/deerflow/` is the source anchor even though the manifest is above it.
   - Treat top-level operational directories such as `scripts/` as independent anchors.
   - At every anchor, initially emit every immediate code-bearing child as a candidate bucket. Also emit a synthetic direct-files bucket for files directly inside the anchor.
   - Recursively split a candidate when it has at least two significant code-bearing children and one of these holds:
     - it crosses an explicit boundary;
     - direct files are less than roughly 25% of its code, meaning it is mostly a container;
     - it exceeds a calibrated budget, initially `1,500 non-test LOC OR 20 source files`.
   - Define a significant child initially as `>=200 LOC OR >=5 source files`, unless an explicit boundary or risk hit forces it to remain separate.
   - When splitting, replace the parent’s recursive bucket with child buckets plus a non-recursive direct/residual bucket. Never leave both an unrestricted parent and its children.
   - Use a soft depth ceiling of four levels relative to the source anchor. An oversized bucket at that depth becomes an advisory “manual split required,” not a silently accepted leaf.
   - Roll homogeneous families up before recursion so locales, fixtures, generated bindings, and migration histories do not explode the frontier. They still receive explicit family items; they are not silently ignored.

   This would seed:

   - pi: every `packages/*/src/*`, including `utils/` and `cli/`; large/container-shaped `core/` directories then split into their children.
   - deer-flow: `deerflow/*`; `frontend/src/{core,components,app}` and their significant children; `scripts/*`, including `scripts/wizard/`.

   So yes, “exceeds N LOC and has >=2 code-bearing children” is sane—but only as one fallback trigger. Used alone, it still misses small boundaries and mistakes structural containers for subsystems.

   Two important invariants:

   - Every included production file belongs to exactly one FS leaf bucket.
   - Every exclusion or family rollup is explicit and reproducible.

2. **Migration matching: do not let normalized containment certify coverage.**

   I would use three confidence tiers:

   - **Accepted migration evidence:** an exact repo-relative path, exact glob, or a unique component-aligned path suffix containing at least two components.
   - **High-confidence suggestion:** a unique exact basename with extension, extracted from path-shaped Markdown such as links, backticks, or code-map cells.
   - **Candidate only:** camel/kebab/snake splitting, singular/plural normalization, light stemming, and separator-stripped comparison.

   The last tier fixes discovery suggestions such as `credential-store.ts` ↔ “credential stores” and `update_agent_tool.py` ↔ `update_agent`, but it must not mark an item rowed. Across 300 KB of prose, normalized containment will eventually produce convincing accidents.

   Therefore I disagree with the proposal if both sides of the `OR` count as rowed:

   - Component-aligned, unique path-suffix matching: acceptable for automatic migration.
   - Separator-stripped stemmed containment: suggestion only.
   - Anything not accepted becomes `unresolved`, not `covered`.

   The eventual gate should never run this matcher. Migration produces the sidecar’s exact mappings; the gate reads only those mappings. This keeps migration ergonomics and gate precision separate.

3. **Risk denominator refinements.**

   **a. Tests:** do neither extreme.

   - Suppress individual test files from production-risk findings by default.
   - Emit one test-family item per ownership root/package, not one repository-wide `tests` item.
   - Preserve separately executable integration, security, release, and end-to-end harnesses as their own surfaces when appropriate.

   Tests remain coverage evidence and a documented subsystem, but they stop overwhelming the actionable risk list.

   **b. Rollups:** migrations yes; workflows generally no.

   Good family-level units include:

   - migration/revision histories, with count or digest recorded;
   - fixtures and seed datasets;
   - localization catalogs—important because deer-flow’s i18n omission shows they cannot simply be excluded;
   - generated clients/bindings and schema snapshots;
   - vendored trees;
   - homogeneous examples/templates.

   Keep these finer-grained:

   - CI workflows: each file is independently triggered and can have different permissions, secrets, or runners. The pi credential falsehood argues directly against one `.github/workflows/` bucket.
   - Deployment: roll up by independently deployable stack/environment, not one global deploy directory.
   - Public route handlers, executable scripts, and entrypoints: individually or by their authoritative registry.
   - Destructive migrations/backfills: allow exceptional files to become additional risk items even when the migration family is rolled up.

   **c. Missing risk/critical-surface classes:**

   The prototype omitted several charter classes and several classes implied by the known findings:

   - entrypoints and independently executable operator/admin scripts;
   - tool, provider, command, permission, and feature registries;
   - destructive file/database operations;
   - untrusted-content ingestion: uploads, clipboard, MIME/media parsing, EXIF, archives, codecs/WASM;
   - model/provider resolution, routing, fallback, and catalogs;
   - runtime composition/factories/middleware assembly;
   - framework-conventional routes such as Next.js `app/**/route.ts`;
   - sandbox tools with filesystem, network, or process capability;
   - hidden extension/config roots such as `.agent/skills`;
   - privacy/telemetry configuration and identifiers.

   “Risk denominator” may now be too narrow a name. `critical_surface` better captures model resolution, runtime assembly, and extension registries, which are consequential without necessarily being security risks.

   The inside-file findings must remain a separate closed-enumeration mechanism. Do not pretend broader filename patterns solve `glob`, `grep`, `skill_manage`, or `RuntimeFeatures`.

   **d. Content/API signals:** yes, but advisory and scored.

   Path names should be only one signal. Add production-code capability detectors for:

   - subprocess execution;
   - network clients, proxy configuration, and global `fetch` replacement;
   - file deletion, permission changes, and atomic replacement;
   - keychain/credential/secret APIs;
   - environment access paired with secret-like keys;
   - route registration/decorators;
   - telemetry SDKs;
   - dynamic imports/plugin loading;
   - package-manager/install calls;
   - migration or destructive DDL.

   Require paired evidence where possible—import plus call, registration plus exported handler, or capability plus entrypoint reachability. A lone `os.environ` or `fetch` call is far too common.

   These detectors generate inventory candidates; they never gate discovery. Once accepted into the frozen inventory, exact reconciliation can gate them. Built-in critical findings should also require an explicit waiver to exclude, so an author cannot quietly tune away inconvenient results.

4. **Schema: canonical JSON sidecar, rendered Markdown appendix.**

   I strongly prefer a sidecar over parsing a Markdown table. Specifically, JSON is attractive here because the validator is pure Python: it adds no YAML dependency, has fewer implicit types, and supports deterministic serialization. LLM agents can author it reliably enough when the validator produces focused schema errors. Human readability belongs primarily in the rendered appendix.

   Separate discovery items from coverage rows:

   ```text
   schema_version
   generator_version
   snapshot_commit
   discovery_config
   inventory_items[]
     id, scope/path, recursive, denominators, surface_type, risk_classes
   coverage_rows[]
     id, inventory_item_ids, disposition, guide_evidence, source_evidence
   exclusions[]
     scope, reason, provenance
   ```

   Additional rules:

   - One canonical owning row per inventory item; optional related rows may be references.
   - Many items may share a row only with an explicit grouping reason.
   - Every risk-critical item remains visibly enumerated even when grouped.
   - Reject overlapping FS scopes unless expressed as parent exclusions/carved children.
   - Recompute inventory at the snapshot commit and compare it with the stored inventory.
   - Render the appendix table between generated markers; validation fails if it is stale.
   - Reject unknown fields and duplicate keys.

   A strict Markdown table is initially convenient, but it couples correctness to escaping, column order, wrapped text, formatting edits, and parser edge cases. That is exactly the brittleness the charter is trying to remove.

5. **Experiment 2: split it into four measured lanes before specifying v6.**

   **Corpus:** run pi, deer-flow, qm, prime-agent, hermes, and cosmos. Do not assume that satisfies structural diversity. If those six do not include each category, add one real infra-heavy repository and one generated-code-heavy repository; also add a small single-package repo if none of the existing set supplies an over-fragmentation control.

   **Lane A — raw inventory quality, without guide matching:**

   - Verify deterministic repeatability.
   - Verify 100% assignment of included production files to exactly one FS bucket.
   - Record overlaps, uncovered direct files, bucket count, LOC/file distribution, oversized opaque buckets, and tiny-fragment rate.
   - Measure recall separately for FS, critical-surface, and their union.
   - Pre-register the known file/directory target set:
     - pi: six of six—image ingestion, HTTP dispatch/proxy, model resolver, analytics, session-analysis scripts, self-update.
     - deer-flow: four of four—wizard, i18n, memory routes, `deerflow/utils`.
   - Do not score the three inside-file findings as denominator false negatives.

   **Lane B — reconciliation matcher:**

   - Hand-label every inventory-item/guide relationship on pi and deer-flow.
   - Stratify and label at least 50 items on each remaining repo.
   - Report precision and recall separately for exact paths, component suffixes, unique basenames, and normalized lexical suggestions.
   - Require 100% precision for anything automatically migrated as rowed. Fuzzy suggestion recall can be high without affecting gate precision.

   **Lane C — noise and author burden:**

   - Adjudicate every unrowed risk finding, not only known positives.
   - Measure actionable precision before and after test suppression, family rollups, and token-safe matching.
   - Record inventory items and manual migration decisions per 10 KLOC.
   - Track time/decisions required to migrate each guide. A mechanism with good recall but hundreds of low-value dispositions is not ready.

   **Lane D — exact gate and update behavior:**

   Mutation-test:

   - missing mapping;
   - stale/nonexistent path;
   - overlapping glob;
   - recursive parent without carved children;
   - unjustified exclusion;
   - stale rendered appendix;
   - snapshot mismatch;
   - legacy schema;
   - added surface;
   - renamed surface;
   - removed surface with a stale row.

   Also run a separate minimal closed-enumeration experiment against the three deer-flow inside-file findings. Its results should not be blended into denominator metrics.

   I would proceed to the spec only if:

   - the FS partition has zero uncovered/overlapping included files;
   - the union catches all ten known file/directory omissions;
   - automatic migration has zero false “rowed” decisions;
   - exact reconciliation has zero false blockers on correctly migrated guides;
   - advisory noise is low enough that migration remains reviewable;
   - repeated runs are byte-stable.

The main design conclusion is unchanged from the [charter](/home/xteom/Documents/cura/ranoa-skills/docs/2026-08-13-v6-coverage-denominator-charter.md): promote schema validation, path existence, snapshot consistency, and exact bidirectional reconciliation. Keep bucket discovery, capability detection, and prose migration advisory until their separate measurements justify more.