# Field review: dpi-harness-loop hackathon → autonomous-subgoal-loop v4

**Date:** 2026-08-19. Three Fable reviewers examined the hackathon repos in
`~/Documents/cura_hackathon/` (dpi-cura-issemym-{architecture,harness-medico,
harness-usuario}), where `dpi-harness-loop` — a single-file, facts-baked-in,
project-specialized sibling of our skill — ran for real (33+ commits, 8+ PRs,
multi-repo hub-and-spokes coordination). Mateo adopted all four improvement
themes. Full reviewer reports live in the session transcripts; this file keeps
the decisions and their strongest evidence.

## Validated (no change needed)

- Write-ahead intents, step-named checkpoint commits, fresh adversaries with
  verdict obligation (66 findings across four gates; "35 concrete findings
  against work that looked finished from the inside" — usuario morning
  report), done-with-evidence, decide→document→continue: all ran, all paid.
- **Session records**: the field lacked them and paid — medico reached G10
  with central status "(No sessions yet.)"; usuario ran a recordless second
  session. Our open-record-first + dead-run reconstruction is field-vindicated.
- **Plan-owns-the-facts**: facts baked into the skill rotted within 20
  minutes of seeding (usuario sync commits `406d3b1`, `bc74dd0`); every
  restated constant drifted from its authority.

## Adopted themes

**T1 — Core fixes (16):** coverage matrix (external criterion → owning
subgoal + visible cannot-verify list; evidence: nine silently ownerless
binding criteria); next-executable-subgoal pointer with exact acceptance
command, atomic with state changes; write-ahead as dedicated commit with the
prediction preserved at close; one branch = one coherent increment (batching
with written justification; the strict rule was dead on arrival); commit
before destructive verification + mutation testing as gate-2 instrument (an
hour lost to `git checkout --` mid-mutation-run); review slots anchored to
git ranges (findings lists otherwise vanish — usuario's 17 G1 findings are
unrecoverable); state+evidence in one commit (a `done` cited a review still
running); Plan merges to integration before any code branch; pointer-to-
authority for restated constants + drift readiness check; relocatable
reading-map paths + environment smoke checks (every upstream path was fiction
on the real machines — issue #5, I-08/I-09); cached-facts-with-provenance;
follow-up-subgoal children keep `done` immutable; subgoal-id threading
through branch/commits/PR; reports-index row at session open; seed-file
lifecycle statements (`04cd08c` fixed an agent shunning its own session
prompt); tests-that-bind guidance (green suites hid live defects; `ttft_ms`
measured 0 on the wrong span).

**T2 — Seeded bootstrap:** facts-pack path (KICKOFF.md pre-answered every
interview topic → 11 PRs merged unattended in one session; our text forbade
exactly this); each seed answer logged "answered by seed <path>", interview
only gaps, external-write policies only with explicit seed authorization;
bootstrap emits a portable START.md-style session prompt (<4,000 chars);
Plan creation recorded as subgoal zero with adversarial verdict + merge
evidence (medico G1: `da4185e`→`7b1151a`→PR #1).

**T3 — Skill-sync intake:** version-stamp the skill in the Plan; loaded-skill
vs stamped-version divergence = a proposed ruleset change through adversarial
intake, never silently followed (hand-synced copies faithfully propagated a
canonical contradiction — two competing allowlist authorities survived two
syncs into both repos).

**T4 — Multi-repo hub-and-spokes mode** (new references/multi-repo.md):
ADR-S09's design, plus fixes for what broke — closed PR write-channels into a
hub that holds only contracts/ADRs/deliverable-bar/protocol; the external bar
as a record type ("the bar, not the plan"); status appends folded into the
morning-report step (a reminder alone failed); parity protocol
(fetch-before-claiming, adopt-ledger — usuario adopted 8 sibling designs and
found a defect in its own code by reading medico's; convention-setter + early
parity handshake, since role assignment alone allowed a seven-point
divergence); non-blocking escalation with interim decisions (PRs #15/#16
open at session close; I-08's interim decision is the model); machine-
readable shared interfaces (prose contracts produced `delivery` vs
`delivery_mode`); digests as a first-class reading-map entry between pointer
and copy.
