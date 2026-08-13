# v6 — Coverage Denominator: design charter

Date: 2026-08-13. Status: charter for the NEXT design cycle — not yet designed, not yet implemented. Sources: the validation report's coverage findings + an independent cross-model review (OpenAI Codex, codex-cli 0.146.1) of the roadmap, which reshaped this substantially.

## Problem (evidence-backed)

Every silent omission found across four guide audits lived in a source subtree the coverage matrix had **no row for**. The disclosure machinery never lied; the inventory upstream of it under-enumerated ("no row → invisible"). Additionally, the skill's update flow scopes work by intersecting changed files with already-cited paths — definitionally unable to discover never-cited new surfaces — so update mode currently perpetuates the defect.

## The gateable invariant (per the codex review — narrower than first proposed)

> Every item in a deterministic, explicitly configured inventory must map by exact repo-relative path to a coverage row with one of the allowed dispositions (covered / summarized / omitted-with-reason).

- **Gate the reconciliation, not the discovery.** Deciding what belongs in the inventory is heuristic → advisory. Checking that inventory items map to rows (and rows map back to existing paths) is exact → gateable, after calibration.
- **Exact paths or explicit globs only.** No fuzzy basename resolution in this gate (the LOC check's any-candidate resolution is fine for its purpose; it is wrong here).
- **Bidirectional:** every inventory item → a row; every row → existing inventory items. Parent rows must declare whether they cover recursively and list carved-out children (a single `src/` row must not mask heterogeneous subtrees).

## Two denominators

1. **Filesystem/package denominator** — recursively bucketed at ownership boundaries (packages, workspaces, top-level dirs), not a flat size-thresholded dir list. Size thresholds alone fail twice: they admit noise (locales, generated code) and miss small, high-risk surfaces.
2. **Risk denominator — inventoried regardless of LOC:** CI workflows, deployment manifests, entrypoints, auth/credential surfaces, self-update/install paths, public route registries, tool/provider registries, network interception, persistence migrations, destructive operations. (The false hosted-CI-credentials claim and the remote-JSON self-update path were both sub-threshold by size.)

## Coverage schema (prerequisite)

Rows need: stable ID, exact path/glob, disposition, evidence link, surface type, risk class, snapshot commit. Prefer a machine-readable inventory (sidecar or canonical table format) rendered into the appendix over heuristic Markdown scraping — validator brittleness grows with every gate that parses loose prose.

## Calibration protocol (before any gate promotion)

Shadow/advisory mode against pi, deer-flow, qm, prime-agent **plus structurally different repos** (monorepo, mixed-language, infra-heavy, generated-code-heavy). Record false positives AND false negatives. Promote only the demonstrably precise portion. (Same discipline that demoted the concept-level inward checks in v5 — apply it up front this time.)

## Also in v6 scope

- **Full-tree update discovery:** update mode must inspect added/renamed paths against the inventory before intersecting diffs with citations.
- **Closed-enumeration evidence rule (narrowed):** consequential closed sets only — commands, tools, routes, providers, permissions, deployment modes, state stores, security controls — each must cite its source-of-truth registry; not every "the X are:" sentence.
- **Security-claim evidence rule:** trust-boundary, credential-presence, network-access, and negative security claims require scoped evidence including workflow/deploy/config sources. (A checklist sentence demonstrably did not prevent the false CI claim; the rule must demand the evidence artifact.)
- **Validator/schema versioning:** stamp the appendix schema version; define explicit legacy behavior so v5-era and hand-tuned guides fail with "needs migration", not a wall of new errors.
- **Acceptance criteria for refreshed guides** (replacing letter-grade targets, which are single-reviewer-noisy): all known defects resolved; zero unmapped inventory items; all risk-critical surfaces explicitly dispositioned; no unsupported security absolutes; no stale finding dispositions.

## Explicitly rejected (with reasons)

- **"Assumed background" README statement as an enforcement mechanism** — converts defects into prerequisites; grade-gaming vector against the skill's zero-to-expert promise. Purely descriptive audience notes remain fine.
- **Hard-gating the raw size-thresholded dir sweep** — the coarse form false-positives (noise trees) and false-negatives (small risky surfaces) simultaneously.
- **Phrase-blacklisting as the completeness-claim control** — synonyms are trivial; the real control is the scope-statement requirement (shipped in v5.1). A validator tripwire on the known phrases is acceptable as a warning only.
- **Panels on every generation** — reserve 2–3-reviewer panels (union-of-findings + adjudication, never averaged letter grades) for milestone audits and high-risk guides.

## Already shipped ahead of this charter (v5.1)

Critic scope-statement requirement + completeness-claim prohibition; verdict-immutability + current-disposition-table finalization invariant (SKILL.md). The pi guide's known falsehood (hosted-CI credentials) and hook-mislabel were hotfixed on `guide-v3` rather than waiting for v6 — known misinformation does not wait for a redesign.

## Sequencing

1. pi hotfix (done alongside this charter) → adopt retrofitted guides.
2. Design cycle for the schema + reconciliation (this charter → full spec → review).
3. Shadow-mode calibration across ≥6 repos.
4. pi/deer coverage refreshes under the calibrated contract.
5. Gate promotion for the precise subset; qm/cosmos/hermes migration under the versioned schema.
