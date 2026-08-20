# The Plan: properties, required records, readiness, repair

No fixed file layout — structure is designed at bootstrap and restructured
whenever growth demands (split files under `docs/`, create indexes, whatever
the project needs). What is fixed are the **properties**, **required
records**, and the **readiness contract** below. When in doubt about
structure: what does the *next fresh agent* need to read for its subgoal?
Optimize for that reader. The Plan exists for them, not to look complete.

## Properties

1. **Cold onboarding.** A fresh agent reads `docs/PLAN.md` and within minutes
   knows: what the system is, what to read in what order (and what NOT to
   read), where the project is going, and the next executable subgoal.
2. **Anti context-rot.** Short files; pointers to sources instead of copies;
   no long summaries that go stale. A Plan file that's costly to read fully
   must be split — that's a signal, not an option.
3. **The Plan stays general.** The durable Plan never contains detailed
   design or code. Bounded *operational* artifacts (a subgoal's execution
   plan) are permitted, referenced from their subgoal, and archived or pruned
   when the subgoal closes.
4. **Verifiable state.** Every subgoal carries the required fields below.
5. **Lossless evolution.** Restructuring is expected and allowed anytime — it
   passes adversarial review, loses no information, and `docs/PLAN.md`
   remains the entry point.

## Marker

`docs/PLAN.md` begins with the exact line:

```
<!-- plan: autonomous-subgoal-loop -->
```

A `docs/PLAN.md` without this marker is foreign by definition → repair mode.

## Required records

**Mission:** what the system is; what "done overall" looks like (1–3 lines).

**Skill stamp:** the content hash of the skill the ruleset was compiled from
— computed as `cat SKILL.md references/interview.md references/loop-playbook.md
references/plan-template.md references/multi-repo.md | sha256sum` from the
skill's directory — recorded with the date. Loop mode recomputes with the
same command. Divergence intake (SKILL.md invariant 5) produces an **intake
record**: from-hash → to-hash, summary of the semantic diff, safety delta,
adversarial verdict, accept/reject, effective-from; stamp, ruleset lines, and
the decision entry change **atomically in one commit** on accept, and a
rejected hash is recorded so it never re-fires intake.

**Next action:** one tagged line — `recover SG-x` (in-progress/dead-run
state) · `execute SG-y — <exact acceptance command>` · `none —
complete | dependency-blocked | focus-exhausted | global-blocker` — kept
accurate **in the same commit that changes subgoal state**. It is a cache of
the selection rule, never an authority: on mismatch the backlog wins and the
mismatch is logged as an inconsistency.

**Coverage matrix** (required whenever topic K declared an external bar):
records the bar's source + revision/hash and enumerates its criteria with
stable IDs — readiness compares that denominator against the matrix. Every
criterion has an accountable owner: the subgoal that proves it, or (under
topic L) `owned by <spoke>`, kept current by the parity protocol.
"Cannot verify" is a **proof state, not an ownership substitute**: such an
entry still has an owner, plus blocker, reason, and resolution owner. The
bar is decomposed by the backlog, never edited by it.

**Sources of truth:** the authority-by-domain table (source → domain it rules)
plus the conflict rule in force.

**Scope boundary:** where our domain starts/ends; what we build; what lives
outside and who owns it; what we simulate and from which spec.

**Ruleset** — the full effective ruleset, one line per rule, versioned via
decision log. **Completeness contract:** there is at least one rule line for
*each* interview topic A–L (K/L may be "not applicable", dated), plus the
safety-floor restatement and the
mechanical invariants. A topic the project disabled or overrode still gets its
line, with the dated decision (`R7 testing: e2e-first default REPLACED by
contract-tests-only, see D-014`). A missing topic line = not ready. A fresh
agent without the skill resumes from this section alone.

**Allowlist** (exhaustive; unlisted resource OR verb = denied):
```
(dev, dynamodb-table, drp_*,  create|update)
(dev, lambda,         drp_*,  create|update|invoke)
(git, feature-branch, sg-*,   push)
(git, feature-branch, sg-*,   delete-merged-feature-branch)  # verb's preflight: ref matches prefix, fully merged into integration, never the integration branch
(git, pull-request,   →dev,   create|merge-on-green-ci)
(git, integration-branch, docs/**, push-plan-state)  # Plan-state only (write-ahead, journals, session records) — exempt from the PR flow; code never rides these commits
```
Deletion and permission-changing verbs appear only with the human's explicit
interview confirmation, and only as their guarded canonical verb — a bare
`delete` on a prefix is malformed.

**Subgoal:** id · objective (1–2 lines, general) · ordered read list (path +
why, only what this subgoal needs) · execution-plan reference (the bounded
artifact gate 1 reviews; archived at close) · acceptance: named test cases +
exact verification command + expected result · **plan-review** (gate 1:
verdict + findings→resolutions, or the explicit verified list) · **diff-review**
(gate 2: same schema, plus the reviewed branch/commit) · **evidence** (set at
close: date, command as run, actual result, and merge SHA/PR when the git
policy requires integration) · status `pending | in-progress | done | blocked`
· dependencies (subgoal ids) · step journal (one line per completed loop step)
· write-ahead intent while in-progress ("attempting X, expect Y").
Each review slot is filled **when its gate completes** — not deferred to
UPDATE, where a crash would orphan the verdict into journal prose.
Status transitions are conditional: `done` requires evidence + both reviews
recorded with no unresolved findings, and is set **after** the merge it
references. `blocked` requires: diagnosis, exact state, hypotheses tried,
options, recommendation, scope (local | global).

**Decision log:** date · decision · why · discarded alternative — one line
each. Includes every nocturnal "assumption to validate" and every ruleset
change (old version → new version, adversarial verdict, effective from the
next subgoal).

**Lessons & surprises** (append-only, parsimonious): expectation → observation
→ propagation (which sections/subgoals it invalidates; the next BRIEF
verifies). Recurrences increment/link the existing entry and open an
Inconsistencies item.

**Inconsistencies:** source · description · proposed resolution · status.

**Open problems / blockers:** including blocker scope (local | global).

**Reading map** (global onboarding): ordered entries — path · purpose · read
fully or which part — then a separate do-not-read list (e.g. `legacy/`);
credentials as a path only. Paths are repo-relative or explicitly
machine-scoped (never bare absolute home paths — seeds travel); environment
facts carry a smoke command sessions run at start. Three entry classes:
pointer (default) · **digest** (a distilled heavy source, with source path +
read date) · cached facts, only under a provenance header of the form
"cached from <source> on <date>; on conflict the source wins". Any restated
constant anywhere in the Plan names its authority the same way — restatements
without a deferring pointer are how summaries drift into law.

**Sessions & morning reports:** each session opens a session line (id, date,
focus, status `running`) **and its reports-index row in the same commit,
after only the read-only integrity preflight** (loop-playbook session flow),
and is closed by its morning report (contents per loop-playbook.md). Any
`running` session without a closing report — regardless of subgoal states —
means a dead run: a later session reconstructs its report per
loop-playbook.md.

**Multi-repo records** (required whenever topic L is declared): coordination
manifest — repo URLs, roles, branches, owned path domains, convention-setter
per shared surface, and one integration owner per cross-repo criterion ·
adoption ledger (sibling ideas: adopted / not-yet) · pending escalations,
each with channel, hub PR, **interim decision being proceeded on**, status,
last check · the hub write channels compiled as allowlist entries including
their merge verbs (e.g. `(hub, status-file, status/<spoke>/, create-via-pr)`,
`(hub, pull-request, status/*, merge-on-green-ci)`,
`(hub, pull-request, →main, create)`).

## Readiness contract

Two stages. **Content checks** run on the candidate at bootstrap (before
installing) and on every later invocation; the **installed check** is simply
that the content lives at `docs/PLAN.md` at the git root, marker first line.
Any failure → repair mode:

- [ ] Marker present as first line
- [ ] Mission, sources-of-truth table, and scope boundary present
- [ ] Ruleset passes the completeness contract (a line per topic A–L + safety
      floor + invariants; overrides dated)
- [ ] Allowlist well-formed: every entry has environment, resource type,
      name/prefix, verbs; destructive/permission verbs only in guarded
      canonical form
- [ ] Every subgoal has the required fields; statuses valid; every `done` has
      evidence + both reviews; every `blocked` has its required fields;
      dependencies resolvable (no cycles, no unknown ids)
- [ ] Skill stamp present; next-action line present, well-tagged, and
      consistent with the backlog (recompute the selection rule to check)
- [ ] Coverage matrix present when topic K declared an external bar; its
      criterion IDs match the bar's recorded revision (denominator check);
      every criterion has an accountable owner; cannot-verify entries carry
      blocker + resolution owner
- [ ] Multi-repo records present when topic L is declared (manifest,
      adoption ledger, escalations with interim decisions); every hub write
      channel appears as an allowlist entry
- [ ] Reading map present and ordered; credentials appear as path only; no
      bare absolute home paths; cached facts and restated constants carry
      their provenance/authority pointers
- [ ] Session records well-formed (a dangling `running` session is not a
      readiness failure — it triggers dead-run reconstruction in loop mode)
- [ ] Portable session prompt exists, under 4,000 chars, carries its
      lifecycle line, and its safety digest defers ("the binding floor is
      the Plan's restatement; on conflict the Plan wins")
- [ ] The Plan's safety-floor restatement semantically matches the floor of
      the **stamped** skill version — a drifted or loosened restatement is a
      readiness failure; a delta between stamped and *loaded* skill is the
      intake's business, never a readiness failure
- [ ] No merge-conflict markers, no truncation

## Repair recipe

1. **Classify:** foreign file (no marker) · crashed bootstrap (marker, fails
   content checks, no sessions) · damaged/incomplete Plan (marker, history
   present) · **bootstrap leftovers without an installed Plan** (entry-point
   pointer, START file, consumed seed, or beacon present; no `docs/PLAN.md`)
   — check for write-ahead intents, step journals, session lines.
   For the leftovers class: unattended → stop with a report (pushing the
   beacon if absent, per the floor's sole pre-Plan exception); attended →
   inventory the leftovers, resume the interview/seed from what's already
   recorded, and land the atomic bootstrap increment — a consumed seed's
   external-write grants are never re-applied without re-confirmation.
2. **Preserve:** never overwrite or delete existing content; a foreign file's
   fate (relocate/rename) is the human's call.
3. **If unattended:** stop with a report (what's wrong, options,
   recommendation). Mutate nothing.
4. **If attended:** interview only what's missing or contradicted, compile,
   pass the adversarial design review, re-run readiness, then install.

## Entry-point wiring

If the repo has an agent-instructions file (CLAUDE.md / AGENTS.md), add one
line pointing to `docs/PLAN.md`. The Plan, not that file, holds the content —
the pointer just guarantees discovery by agents that didn't load this skill.
Bootstrap also commits a **portable session prompt** (START-style file,
<4,000 chars: dispatch conditional + safety-floor digest + "start at
docs/PLAN.md") for runtimes without skill loading. Every bootstrap-era prompt
**or seed** file carries a lifecycle line — `reusable, every session` or
`one-time, executed <date>` — so later agents neither re-run kickoffs nor
shun their own session prompt.
