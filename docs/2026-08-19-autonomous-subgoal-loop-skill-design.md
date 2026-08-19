# Design: `autonomous-subgoal-loop` skill

**Date:** 2026-08-19
**Source:** `init-prompt-optimizado.md` (Spanish init prompt for the DRP backend autonomous agent)
**Status:** Approved by Mateo 2026-08-19 (interactive brainstorm; decisions recorded below)

## Summary

A framework skill for plan-driven autonomous agent work on a project. One entry
point, two modes. Its central object is **the Plan** — a planning documentation
system under `docs/` in the *target* repo, entry point `docs/PLAN.md`. Agents
are disposable; the Plan is the persistent brain. Everything about how a given
project runs is decided in a bootstrap **interview** and persisted into the
Plan; the skill ships the battle-tested defaults from the source doc.

## Decisions (from brainstorm)

| Question | Decision |
|---|---|
| Lifecycle | One skill, mode by state: `docs/PLAN.md` absent → bootstrap; present → loop |
| Inputs | Interview → persisted into the Plan itself. Loop mode needs zero inputs |
| Fixed vs configurable | **Everything interviewable** (framework), with the source doc's ruleset as defaults; minimal invariant core |
| Call syntax | Bare invocation + optional free-text focus arg; reserved keyword `reconfigure` |
| Language | English body; Spanish original kept as reference |
| Name | `autonomous-subgoal-loop` |

## Invocation contract

- `/autonomous-subgoal-loop` — invoked **inside the target repo**. Mode by state:
  - `docs/PLAN.md` absent → **bootstrap mode** (interview + investigation + Plan creation).
  - `docs/PLAN.md` present → **loop mode** (read Plan, execute subgoals under its ruleset).
- Optional free-text arg = session focus (e.g. `only subgoal 3`, `stop after two merges`).
- Reserved keyword **`reconfigure`**: re-opens the interview (whole or named
  section) even when the Plan exists. Ruleset changes are a Plan change like any
  other: adversarial review + decision-log entry, no information loss.

## Invariant core (the only things NOT interviewable)

1. **`docs/PLAN.md` is the stable entry point.** Every fresh agent starts there,
   forever. Restructuring is allowed anytime as long as the entry point holds and
   no information is lost. (This is also what makes mode-by-state work.)
2. **The ruleset lives in the Plan**, compactly — one line per policy decision,
   not prose copies. A fresh agent resumes from the Plan alone, even without this
   skill installed.
3. **Interview answers are persisted before any code work starts.**

Everything else — including the loop shape itself — is a default the interview
can override.

## Bootstrap mode flow

1. **Interview** — one topic at a time, each question presenting the default;
   accepting all defaults reproduces the source doc's ruleset. Facts (paths,
   scope, allowlist) have no defaults and must be answered.
2. **Investigate** — the repo, each declared source of truth, and the convention
   repos (how *they* organize docs), before designing anything.
3. **Design the Plan system** — structure is the agent's decision, informed by
   investigation. Passed through an **adversarial fresh-context subagent** with
   verdict obligation: can a truly fresh agent resume from this? Does it scale or
   become a monster file? Where will it rot?
4. **Write the Plan** — including the ruleset section, sources-of-truth table,
   scope boundary, resource allowlist, reading map, and an **initial subgoal
   backlog** with verifiable acceptance criteria.
5. **Report** — what was decided, what was assumed (marked "assumption to
   validate"), what the first executable subgoal is.

## Interview schema (topics A–J)

**F** = fact, must be answered; **P** = policy, has a default.

| # | Topic | Asks for | Default (from source doc) |
|---|---|---|---|
| A | Mission | **F:** what the system is; what "done overall" looks like | — |
| B | Sources of truth | **F:** table of source → authority *domain* (the WHAT / the current HOW / conventions / historical-only) | **P:** conflict rule: cross-domain → that domain's authority wins; intra-domain or uncovered → log in Inconsistencies with proposed resolution, decide by general engineering criteria, continue without stopping. Docs have errors and bias: judge by internal + external consistency |
| C | Scope boundary | **F:** where our domain starts/ends; what we build; what lives outside; what to simulate and from which spec | **P:** simulate external inputs minimally; formats come from the spec source, never invented |
| D | Hard constraints | **F:** environments + which are touchable; cloud resource allowlist; credentials location | **P:** dev-only; allowlist declared explicitly in the Plan, everything else prohibited without interpretation; credentials referenced by path only, never copied; everything in containers; total freedom locally, the hard limit is only outward |
| E | Code policy | — | **P:** no hardcoding, every parameter explicit; minimum necessary but correct and useful e2e; simple > complex; general > particular |
| F | Strategy | — | **P:** walking skeleton first (phase 0: full e2e piping with trivial logic), then real logic feature by feature |
| G | Testing | — | **P:** e2e first, several covering different edge cases; minimal unit/integration focused on edge cases, not coverage theater; local in container → push → CI; folder layout per convention repos |
| H | Git flow | **F:** integration branch name | **P:** short GitHub flow; one branch = one subgoal; small checkpoint commits (message = which loop step completed); stacking only when justified, max 2 levels; never force-push the integration branch; auto-merge on green CI, no human approval; red CI → iterate with a NEW hypothesis per retry, else park the subgoal and return later with a fresh subagent |
| I | Autonomy | **F:** any project-specific additions to the stop-list | **P:** decide → document → continue; never stop for style/naming/test-scope/resolvable ambiguity; closed stop-list: ① security/credentials/destructive or out-of-env ops, ② outside scope or allowlist, ③ irreversible + indecidable from any source of truth; blocked → park + move on; before ending, revisit parked subgoals once with fresh eyes; **mandatory morning report**, always, even if the run died |
| J | Loop shape & Plan properties | — | **P:** the 8-step cycle (BRIEF w/ write-ahead intent → PLAN w/ acceptance criteria fixed *before* implementing → EXECUTE → ADVERSARY w/ verdict obligation → TEST (modifying an existing test requires logged justification) → CLEAN → REFLECT 3–6 lines → UPDATE: `done` only with evidence executed this session); fresh subagent per subgoal; Plan properties: cold onboarding, anti context-rot (pointers not copies; splitting a costly file is a signal, not an option), verifiable state (`pending | in-progress | done | blocked`), system memory (decision log, lessons, inconsistencies, open problems, reading map), lossless evolution |

## Loop mode flow

Read `docs/PLAN.md` → morning report of last run (if any) → pick next executable
subgoal → run the cycle the ruleset defines, one **fresh-context subagent per
subgoal** → repeat until no executable subgoal remains (or session-focus arg
says otherwise) → revisit parked subgoals once → write the morning report. The
skill's reference file carries the full default playbook; the Plan's ruleset
records deviations.

## Skill file layout

```
autonomous-subgoal-loop-skill/
  SKILL.md                 # frontmatter, dispatch, invariants, call syntax (lean)
  references/
    interview.md           # full interview schema + defaults (topics A–J)
    loop-playbook.md       # default loop + autonomy rules + git flow, in full
    plan-template.md       # mandatory Plan properties + compact-ruleset format + examples
```

Frontmatter description (triggering conditions only, per writing-skills SDO):
*"Use when starting or resuming autonomous agent work on a project —
overnight/unattended runs, plan-driven multi-session development, bootstrapping
a docs/PLAN.md planning system, or executing subgoals from an existing Plan."*

Deployment: copy `autonomous-subgoal-loop-skill/` →
`~/.claude-cura/skills/autonomous-subgoal-loop/` (repo convention).

## Testing plan (writing-skills TDD)

Three scenario families, baseline (RED) before the skill exists, then with the
skill (GREEN), in a mock target repo:

1. **Bootstrap:** mock repo + "set up autonomous overnight work" → baseline
   agents are expected to skip the interview, invent structure, and bake in no
   ruleset.
2. **Cold resume:** fresh agent + the produced Plan only → can it identify and
   execute the next subgoal without asking anything?
3. **Discipline under pressure:** temptation to mark `done` without executed
   evidence / adversary saying "looks fine" → verify the verdict-obligation and
   evidence rules hold.

REFACTOR: capture rationalizations verbatim from testing, add counters, re-test.
