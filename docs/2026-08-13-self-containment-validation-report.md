# Self-Containment Enforcement — Validation Report

Date: 2026-08-13. Companion to `2026-08-13-self-containment-and-coverage-enforcement-design.md` (§7 protocol). Implementation commit: `6564654`.

## Phase A — validator regression on the four existing guides

Unit tests: 15/15 green (7 new). Live runs (read-only) against pi-v2, deer-flow-v2 (guide-refresh worktrees), qm, prime-agent:

- **All labeled defects flagged:** pi `thinkingLevel` (strong candidate), `branch summary` (strong), `background bash` (weak); qm `processes/ ~480` (LOC gate), `onboarding/` → 06/09 (pointer gate).
- **Every gate error hand-verified real** (or the expected-structural missing `Self-containment review` section on pre-existing guides). Zero false gate errors after tuning.
- **Five NEW real nits found beyond the audits:** qm `skills/ ~1,527` vs actual 1,904 (LOC), qm `templates/`, `src/aws-lease.ts`, `egress-proxy-pub/` pointer mis-routes (target files verified zero-mention), deer-flow `reflection/` → 02 mis-route.
- **Enforcement amendment (recorded in the design spec §4):** concept-level inward findings demoted to a tiered advisory ledger after ~90% FP rate on real prose; the gate keeps what proved precise (LOC, pointers, section/waiver structure).
- Tuning that survived contact with reality: plain-prose-vs-backtick discrimination, punctuation-aware copula, line-initial definition discovery, appendix-is-back-matter rule, any-candidate LOC resolution, first-cell-only path extraction.

## Phase B — retrofit runs (update mode, in-place on `guide-v3` branches)

| Repo | Branch/commit | Validator | Ledger triage | Audit findings |
|---|---|---|---|---|
| pi | `guide-v3` @ `56621ab79` (+107/−29, 16 files) | exit 0 | 10 fixed / 30 dismissed-with-reason | all 7 fixed, source-verified |
| deer-flow | `guide-v3` @ `04e02d2f` (+87/−27, 16 files) | exit 0 | 20 fixed / 53 dismissed-with-reason | all fixed incl. `AuthMiddleware` at both sites + `reflection/` repointed to 07/10 |

Both fresh Phase-B critics found NEW real issues beyond the ledger (pi: extension-path-precedence contradiction, `stream`/`streamSimple`, `/cl`; deer: DooD, product tiers, RunStore/RunRepository) — fixed and logged. Zero waivers used on either guide: every real forward-running term got an inline gloss instead.

## Phase C — blind re-review (8 independent Opus reviewers, neutral randomized paths, no version/baseline knowledge)

| Version | Inward (self-containment) | Outward (coverage honesty) |
|---|---|---|
| pi v2 | **B** (2 blockers: `ModelRegistry`, `!command` two-sense) | B |
| pi v3 | **A−** (1 blocker, pre-existing: `beforeToolCall` mislabel) | B |
| deer v2 | **A−** (0 blockers; near-miss: middleware hooks; `AuthMiddleware` in bumps) | A− |
| deer v3 | **A−** (0 blockers; residue = framework vocabulary) | B |

### Acceptance verdict (spec §7.6)

- **Inward targets met:** pi B → A−; deer A− → A− with substance improvement (v2's bump list = exactly the defects retrofitted; the v3 reviewer *independently verified each fix present at its use site* and found zero blockers).
- **Hand-found defects fixed, confirmed blind:** `thinkingLevel`, `branch summary`, `background bash`, `ModelRegistry`, `preflight ACK` (pi); `AuthMiddleware` (with the family-pattern break), `custom agent`, `SOUL`, DooD, product tiers (deer) — none re-flagged as defects in v3 reviews; several explicitly listed as properly glossed.
- **Outward held in substance:** the retrofit changed no coverage; v2/v3 outward differences are reviewer-sampling variance over a near-identical surface. Neither guide's coverage reaches the qm/prime-agent A− bar — real enumeration gaps exist (below). Grades: pi B→B, deer A−→B.
- **No regressions attributed to the retrofit.** One retrofit-process artifact: pi's `Self-containment review` ledger *understates* the guide (lists three residuals its own author fixed after the critic's verdict) — cheap cleanup.
- **Deviation from §7.5:** the comparator step was performed by the orchestrator rather than a ninth agent — the blindness that matters lives in the reviews (done); the comparison over their grades is mechanical, and re-transmitting eight full reports would lose fidelity.

### New findings for future work (not part of this change)

**pi guide (inward):** `beforeToolCall`/`afterToolCall` presented as extension hooks — actually loop-level config hooks bridged by `AgentSession` to the extension events `tool_call`/`tool_result` (source-verified `packages/agent/src/types.ts#L267,L281`, `agent-session.ts#L424`); "v1" in README:23/26 reads as a prior product version; harness `phase` union never enumerated; stale self-containment ledger.

**pi guide (coverage — for a future coverage refresh):** CRITICAL: self-update path (`package-manager-cli.ts:425-484`) where remote JSON from `pi.dev` supplies the npm package name installed globally — absent from files 19/20 whose job is supply chain; image-ingestion pipeline (~1.3–1.5k LOC, clipboard/EXIF/resize/WASM); global `fetch` override + proxy (`http-dispatcher.ts`); `model-resolver.ts` (704); analytics/privacy plane (`trackingId`, `blockImages`, and a `/privacy` command referenced by the first-run dialog that does not exist in source); session-analysis scripts (~2.9k, also explains the `~4,600` scripts figure being computed over `.mjs/.js` only); **21:96 "Hosted CI is expected to lack developer credentials" is affirmatively false** — `issue-analysis.yml` writes `secrets.PI_AUTH_JSON` to a runner and rotates it back via `gh secret set`.

**deer-flow guide (coverage):** `glob`/`grep` sandbox tools + `sandbox/search.py` missing from ch. 11's enumeration; `skill_manage` tool + `skill_evolution` gate; the second middleware assembly path (`RuntimeFeatures`, `@Next`/`@Prev`, `_assemble_from_features`); `scripts/wizard/` (1,456); frontend i18n layer (1,910); Next.js `/api/memory` proxy route handlers (forward all headers; in tension with 14:41's "only the `access_token` cookie"); `deerflow/utils/`; `.agent/skills/`.

**Skill-level lessons queued (not yet applied):**
1. Critic verdicts must carry a scope statement and never assert a complete residue — both deer outward reviewers independently called the quoted "the findings above are the complete residue" the most misleading sentence in an otherwise honest appendix.
2. Coverage appendices need a **denominator sweep**: reconcile matrix rows against a tree walk so "no row → invisible" can't happen (every silent omission found lived in an unrowed tree; the disclosure mechanism itself never lied).
3. Post-verdict fixes must update the ledger's residual list (pi's stale-ledger artifact).

## Bottom line

The two-tier definitional rule + advisory ledger + expanded critic demonstrably move guides from B to A− on self-containment under blind review, with zero attributable regressions. The deterministic gate holds only checks that survived hand-verification against four real guides. Coverage enumeration is the next frontier and now has a precise, source-verified fix list.
