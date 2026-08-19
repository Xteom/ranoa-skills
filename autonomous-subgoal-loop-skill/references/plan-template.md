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

**Sources of truth:** the authority-by-domain table (source → domain it rules)
plus the conflict rule in force.

**Scope boundary:** where our domain starts/ends; what we build; what lives
outside and who owns it; what we simulate and from which spec.

**Ruleset** — the full effective ruleset, one line per rule, versioned via
decision log. **Completeness contract:** there is at least one rule line for
*each* interview topic A–J, plus the safety-floor restatement and the
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
credentials as a path only.

**Sessions & morning reports:** each session opens a session line FIRST (id,
date, focus, status `running`) and is closed by its morning report (what
merged; what's blocked and why; decisions and assumptions to validate;
refactors; new tests; recommended next attack). Any `running` session without
a closing report — regardless of subgoal states — means a dead run: the next
session reconstructs its report from step journals, checkpoints, and git/PR
state before doing anything else.

## Readiness contract

Two stages. **Content checks** run on the candidate at bootstrap (before
installing) and on every later invocation; the **installed check** is simply
that the content lives at `docs/PLAN.md` at the git root, marker first line.
Any failure → repair mode:

- [ ] Marker present as first line
- [ ] Mission, sources-of-truth table, and scope boundary present
- [ ] Ruleset passes the completeness contract (a line per topic A–J + safety
      floor + invariants; overrides dated)
- [ ] Allowlist well-formed: every entry has environment, resource type,
      name/prefix, verbs; destructive/permission verbs only in guarded
      canonical form
- [ ] Every subgoal has the required fields; statuses valid; every `done` has
      evidence + both reviews; every `blocked` has its required fields;
      dependencies resolvable (no cycles, no unknown ids)
- [ ] Reading map present and ordered; credentials appear as path only
- [ ] Session records well-formed (a dangling `running` session is not a
      readiness failure — it triggers dead-run reconstruction in loop mode)
- [ ] No merge-conflict markers, no truncation

## Repair recipe

1. **Classify:** foreign file (no marker) · crashed bootstrap (marker, fails
   content checks, no sessions) · damaged/incomplete Plan (marker, history
   present) — check for write-ahead intents, step journals, session lines.
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
