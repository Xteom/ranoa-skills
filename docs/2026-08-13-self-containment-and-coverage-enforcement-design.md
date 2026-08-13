# Self-Containment & Coverage-Honesty Enforcement — Design Spec

Date: 2026-08-13
Target: `skills/repo-expert-onboarding` (SKILL.md, `scripts/validate_guide.py`, `scripts/test_validate_guide.py`, critic charter)
Status: awaiting user approval

## 0. Problem statement (what the research established)

Study of five guides (hermes hand-tuned control; machine-generated pi-v2, deer-flow-v2, prime-agent, qm) against their source trees found **two independent defect axes**:

- **Inward — self-containment.** A term is used before it is defined, with no gloss, forcing the reader to jump ahead. The skill has **no mechanism** for this today (its only ordering guidance is "number files in recommended reading order"). Real defects found by hand:
  - *Orphan:* pi's `thinkingLevel` — used in 5 files, defined nowhere.
  - *Wrong-model trap:* deer-flow's `AuthMiddleware` — pattern-matches the ch.05 `*Middleware` family the reader just memorized, but is a different mechanism (HTTP layer); used ch.09, defined ch.16, never disambiguated.
  - *Multi-file gap:* pi's `branch summary` (used 03, defined 09) and `background bash` (03→11), zero gloss at first use.
  - *Two-sense term:* qm's `audience` (token-`aud` vs. conversation participant-set), used load-bearingly in 03/04, both senses defined later, no glossary row despite file 01 disambiguating two other two-sense terms.
  - *Thin definition:* pi's "background bash processes are tracked by the session" — defining-shaped, explains nothing.
- **Outward — coverage.** A live subsystem silently omitted from the guide. The skill's `appendix-coverage-and-evidence.md` **already handles this honestly** (adversarial code-cross-check audits: qm A−, zero silent subsystem omissions; prime-agent A−, one minor one). The hand-tuned hermes guide — which predates the appendix — silently omits ~9 live subsystems including two security chokepoints. Residual machine-guide defects are accuracy nits only: a mis-routed code-map pointer (qm `onboarding/` → files 06/09 which never discuss it), a CLI subcommand present in source but absent from the guide (qm `dev-ci`), a line-count overcount (qm `processes/ ~480` vs. actual 281).

Key calibration findings that shape the design:
- Forward *links* ≠ forward *dependencies*. Heavy forward-linking is healthy navigation; defects are rare and specific. Raw link counts over-predict.
- Real gaps span 6–8 files → a sliding-window check misses them; the pass must be **cumulative**.
- Family-similarity reasoning ("ends in `Middleware`, already covered") *suppresses* the one real blocker → deterministic checks must use **exact-identifier matching only**.
- Weaker reviewer models produce confident false all-clears (a guide-only pass graded hermes A; the code-checking pass found B+ and 9 omissions). Judgment checks need a strong model; cheap-model review of hard judgments is worse than no review.
- Honor-system escape hatches get gamed (historical `Structure rationale: n/a` bypass) → waivers must be substance-checked.

## 1. Prevention — the two-tier definitional rule (SKILL.md)

The highest-leverage piece: the discipline that makes the hand-tuned guide read clean, written down as an authoring rule.

- **First substantive use** of any repo term whose home file is later must carry, in the same sentence, an **inline one-line gloss or an explicit forward link** — ideally both. Enough to follow the current sentence without jumping.
- **Full treatment** at the term's home file.
- **Wrong-model-trap clause:** if a term pattern-matches an already-introduced family but is a different mechanism, disambiguate at first use — "`AuthMiddleware` (Gateway's global HTTP auth layer, **not** an agent middleware — see [16])".
- **Glossary demoted** to an optional back-of-book index ("where is this defined"), explicitly not load-bearing; a first-time reader is never sent to a lookup table to understand a sentence. Definitions live in the prose.
- **Self-containment authoring pass** added to the process (after drafting, before validation): walk files in reading order, maintain a cumulative introduced-terms ledger, and wherever a term runs ahead of its home file, add the inline gloss/link at that spot.

## 2. Detection layer 1 — inward self-containment

Cumulative pass: seed the term ledger from README + file 01, grow monotonically file-by-file, check each file against the **full** accumulated set. Never windowed.

**Deterministic half (`validate_guide.py`) — gated:**
- **Orphan check:** a backticked / PascalCase identifier appearing in ≥3 distinct numbered files with no definition-shaped context anywhere in the guide → error. (Catches `thinkingLevel`.)
- **Strict forward-gap check:** first use of a tracked identifier with zero inline gloss (no parenthetical/appositive in the sentence) AND zero forward link, where the identifier's definition-shaped context first appears in a later numbered file → error, waivable. (Catches `branch summary`, `background bash`.)
- **Exact-identifier matching only.** No suffix/family heuristics, ever.
- Definition-shaped context heuristic: term followed by copula/definition patterns ("is", "means", "refers to", em-dash apposition) or a table row keyed by the term. Precision over recall: when uncertain, do not flag.

**Judgment half (existing critic subagent, charter expanded; Sonnet/Opus-class) — advisory:**
- Thin definitions (defining-shaped sentence that names but does not explain the mechanism).
- Wrong-model traps (family-name collision across different mechanisms).
- Two-sense terms used before disambiguation.
- Lowercase prose terms ("custom agent") that identifier extraction cannot reliably see.

No separate cheap-model (Haiku) filter pass — explicitly rejected: hard judgments demand a strong reader; a false all-clear suppresses scrutiny. If deterministic false positives prove noisy in practice, a local gloss-presence filter may be reconsidered later (YAGNI now).

## 3. Detection layer 2 — outward coverage nit-catchers

The appendix mechanism works; do not rebuild it. Add cheap cross-checks against source:

**Gated:**
- **LOC sanity:** line counts cited in the coverage matrix / code map vs. actual `wc -l` of the cited paths, within ±20% tolerance. (Catches `~480` vs. 281.)
- **Code-map pointer accuracy:** every code-map row that maps a source path to numbered file(s) — the target file must actually mention that subsystem (path or name). (Catches `onboarding/` → 06/09 mis-route.)

**Advisory (ledger):**
- **CLI-command completeness:** subcommands discoverable in source that never appear in the guide. (Catches `dev-ci`.) Advisory because reliable subcommand enumeration is framework-specific; a hard gate would false-positive across ecosystems.

## 4. Enforcement — tiered (confirmed shape)

| Tier | Findings | Action |
|---|---|---|
| **Gate** (`validate_guide.py` exit ≠ 0) | orphans; strict forward-gaps; LOC mismatch; pointer mis-route | Block until fixed or substantively waived |
| **Ledger** (appendix, advisory) | thin definitions; wrong-model traps; two-sense terms; prose-term gaps; CLI completeness | Critic records verbatim; author resolves |
| **Waiver** | any gated finding with a legitimate exception | Must name the term, quote the inline gloss, and state the reason. Validator rejects bare/empty waivers (`n/a`, blank, token-only) |

## 5. Where findings live

New **`Self-containment review`** section in `appendix-coverage-and-evidence.md`, beside the existing `Structure-fit review`: the critic's inward verdict recorded verbatim, plus resolved judgment-findings and any waivers. Gate failures are transient (fixed before completion) and get no permanent home. Validator enforces the section's existence, exactly as it does for `Structure-fit review`.

## 6. Process integration

Current flow: investigate → coverage matrix → file plan → draft → validate (script + critic).
New flow: investigate → matrix → file plan → draft → **self-containment authoring pass (§1)** → validate (**expanded script §2/§3** + **expanded critic §2**) → findings recorded (§5).

After every skill change: commit in this repo (no Claude co-author), then rsync to the installed copy at `~/.claude/skills/repo-expert-onboarding/`.

## 7. Validation protocol (required before the change is called done)

### Phase A — unit + hand-labeled regression (cheap, deterministic)
1. Extend `test_validate_guide.py`: orphan detection; strict forward-gap; waiver substance rejection; LOC mismatch; pointer mis-route; fixture guides both failing and passing each check.
2. **Run the new validator against the four existing machine guides in place** (pi-v2 and deer-flow-v2 worktrees, prime-agent, qm — read-only). Acceptance:
   - Flags the hand-found defects: pi `thinkingLevel` (orphan), pi `branch summary`/`background bash` (forward-gap), qm LOC and pointer nits.
   - Does **not** hard-block qm or prime-agent on anything **beyond** the hand-found defects listed above (false-positive budget: 0 gate errors on those two other than the known nits; new advisory findings are acceptable).
   - hermes is the no-appendix control: validator is expected to fail it on the existing appendix checks; not part of the acceptance budget.

### Phase B — end-to-end re-run of the skill (worktrees)
3. Re-run the updated skill in **update mode** on the two weakest inward guides: **pi** and **deer-flow** (grades B / B+). No new worktrees: work inside each repo's existing `guide-refresh` worktree (`<repo>/.claude/worktrees/guide-refresh/`), on a new `guide-v3` branch created from `guide-refresh` HEAD, editing the guide in place. The v2 guides are committed there, so `git diff guide-refresh..guide-v3` shows every change directly; main checkouts stay untouched. These runs exercise §1 prevention + §6 flow, must fix all gated findings, and must end at validator exit 0. qm and prime-agent (already A− inward) are not regenerated; they serve as Phase-A regression targets only. Writer/updater agents may run on Fable (critical generation work, precedent: prior guide-refresh updaters); everything else Opus/Sonnet.

### Phase C — unbiased re-review and comparison
4. **Blind re-review.** For each re-run guide, copy old (v2, from the `guide-refresh` branch) and new (v3, from `guide-v3`) versions to neutral randomized paths (e.g. `$JOB_TMP/review/G-alpha`, `G-beta`) so no worktree/branch cues leak. Fresh subagents (Opus-class), one per guide-version, with **no knowledge of prior grades, of the skill changes, or that this is a re-review**, run the same two audits used in the study:
   - Inward: self-containment audit (blockers/bumps/orphans, grade A–F).
   - Outward: coverage-honesty audit **with code access** (silent vs. disclosed omissions, grade A–F).
5. **Comparison.** A separate comparator agent receives all blind reports plus the version key and the baseline study grades, and answers: did inward grades improve (target: pi ≥ A−, deer-flow ≥ A−)? Did outward grades hold (≥ A−)? Were the specific hand-found defects fixed? Any new defects introduced?
6. Acceptance: inward targets met, outward held, all Phase-A known defects resolved in the re-run guides, zero unfixed gate errors. If a target is missed, findings return to §1/§2 as design feedback before any wider rollout.

Cost containment: re-run limited to two repos; reviews are one agent per guide-version per axis (8 review agents total) + 1 comparator; Fable only for the two updater agents.

## 8. Out of scope (YAGNI)

- Haiku/cheap-model review pass (rejected — see §2).
- New outward coverage-verification subsystem (appendix already works).
- Sliding-window checking (cumulative ledger instead).
- Case-insensitive placeholder matching (previously rejected on real-guide evidence: lowercase "todo"/"placeholder" are domain words).
- Making the glossary required.
- Re-generating qm/prime-agent/grimoire guides in this cycle.

## 9. Risks

- **Strict forward-gap false positives** (definition-point heuristic misjudges) → gate only the zero-gloss/zero-link subset; precision-over-recall heuristic; substantive waivers.
- **Term-extraction reach** — deterministic sees code-style identifiers only; prose terms depend on the critic. Accepted and documented.
- **Ledger gaming** (empty ledger claiming clean) → critic writes the verdict independently; validator requires the section to exist and be non-stub.
- **Blind-review leakage** (reviewers inferring version identity) → neutral copied paths, randomized labels, no prior context in prompts.
