# The Plan: properties, required records, readiness

No fixed file layout — structure is designed at bootstrap and restructured
whenever growth demands (split files under `docs/`, create indexes, whatever
the project needs). What is fixed are the **properties** and **required
fields** below. When in doubt about structure: what does the *next fresh
agent* need to read for its subgoal? Optimize for that reader. The Plan
exists for them, not to look complete.

## Properties

1. **Cold onboarding.** A fresh agent reads `docs/PLAN.md` and within minutes
   knows: what the system is, what to read (and what NOT to read), where the
   project is going, and the next executable subgoal.
2. **Anti context-rot.** Short files; pointers to sources instead of copies;
   no long summaries that go stale. A Plan file that's costly to read fully
   must be split — that's a signal, not an option.
3. **The Plan is general.** Never detailed design or code. Particulars are
   decided at implementation time; the Plan records direction, state, and
   memory.
4. **Verifiable state.** Every subgoal carries the required fields below.
5. **Lossless evolution.** Restructuring is expected and allowed anytime — it
   passes adversarial review, loses no information, and `docs/PLAN.md`
   remains the entry point.

## Required records

**Ruleset** (one line per rule, complete enough to act on — a fresh agent
without the skill resumes from this alone; versioned via decision log):
```
R1  environments: dev only; integration branch: dev
R2  external actions: deny-by-default; allowlist below is exhaustive
R3  done = verification command fixed at PLAN ran this session, result linked
R4  auto-merge on green CI, no human approval (confirmed 2026-08-19)
...
```

**Allowlist** (exhaustive; unlisted resource OR verb = denied):
```
(dev, dynamodb-table,  drp_*,        create|update)
(dev, lambda,          drp_*,        create|update|invoke)
(git, feature-branch,  sg-*,         push|delete-when-merged)   # integration branch never deletable
(git, pull-request,    →dev,         create|merge-on-green-ci)
```

**Subgoal:** id · objective (1–2 lines, general) · read list (what to read
before starting — only that) · acceptance: named test cases + exact
verification command + expected result · status `pending | in-progress |
done | blocked` · dependencies (subgoal ids) · step journal (one line per
completed loop step) · write-ahead intent while in-progress ("attempting X,
expect Y").

**Decision log:** date · decision · why · discarded alternative — one line
each. Includes every nocturnal "assumption to validate" and every ruleset
change (versioned).

**Lessons & surprises** (append-only, parsimonious): expectation → observation
→ propagation (which sections/subgoals it invalidates; the next BRIEF
verifies). Recurrences increment/link the existing entry and open an
Inconsistencies item.

**Inconsistencies:** source · description · proposed resolution · status.

**Open problems / blockers:** including blocker scope (local | global).

**Reading map:** paths to the spec/handoff, implementation, convention repos —
and what NOT to read (e.g. `legacy/`); credentials as a path only.

**Morning reports:** one per session (see loop-playbook.md).

## Readiness contract

Checked at **every** invocation before loop mode runs; any failure → repair
mode:

- [ ] `docs/PLAN.md` exists at the git root and identifies itself as this
      system's Plan
- [ ] Ruleset present and complete (each rule actionable as written)
- [ ] Safety floor restated (the four items from SKILL.md)
- [ ] Allowlist present and well-formed: every entry has environment, resource
      type, name/prefix, verbs
- [ ] Every subgoal has the required fields; statuses valid; dependencies
      resolvable (no cycles, no unknown ids)
- [ ] Reading map present; credentials appear as path only
- [ ] No merge-conflict markers, no truncation

## Entry-point wiring

If the repo has an agent-instructions file (CLAUDE.md / AGENTS.md), add one
line pointing to `docs/PLAN.md`. The Plan, not that file, holds the content —
the pointer just guarantees discovery by agents that didn't load this skill.
