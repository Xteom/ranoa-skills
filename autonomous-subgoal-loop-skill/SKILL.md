---
name: autonomous-subgoal-loop
description: Use when starting or resuming autonomous agent work on a project — overnight/unattended runs, plan-driven multi-session development, bootstrapping a docs/PLAN.md planning system, or executing subgoals from an existing Plan. Also applies when a repo needs setup so fresh-context agents can work night after night without human review.
---

# Autonomous Subgoal Loop

Agents are disposable; **the Plan is the persistent brain**. The Plan is a
planning documentation system under `docs/` in the target repo, entry point
`docs/PLAN.md`, that carries everything a fresh-context agent needs: the
project's ruleset, state, memory, and next executable subgoal. Every session
validates the Plan by construction — if a fresh agent can't resume from it,
the Plan failed and you've detected it early.

The Plan stays **general** (what to read, how to advance, what was learned,
what's next). Particulars are decided when writing code, never stored in the
Plan as detailed design.

## Invocation

Target repo = the git root of the current working directory (multi-Plan
monorepos are out of scope; if the root looks ambiguous, ask at bootstrap /
treat as a global blocker in a run). Optional free-text argument = session
focus (e.g. `only subgoal 3`, `stop after two merges`). Reserved keyword
`reconfigure [section]` = re-open the interview for an existing Plan.

## Mode dispatch (every invocation)

| State of `docs/PLAN.md` | Mode | Read |
|---|---|---|
| Absent | **Bootstrap**: interview the human, investigate, design and write the Plan | `references/interview.md` |
| Present and loop-ready (passes the readiness contract in plan-template.md) | **Loop**: execute subgoals under the Plan's ruleset; zero inputs needed | `references/loop-playbook.md` |
| Present but foreign, partial, or failing readiness | **Repair**: adopt/complete it with the human if present; in an unattended run, stop with a report | `references/plan-template.md` |

Bootstrap writes `docs/PLAN.md` **last**, after its content passes validation,
so a crashed bootstrap never leaves a loop-ready-looking entry point.

One autonomous session at a time (parallel sessions are out of scope). A stale
`in-progress` subgoal with no live run = a crashed run: recover from its
write-ahead intent and step journal, don't restart blind.

## Safety floor — always in force, never interviewable or reconfigurable

1. Explicit owner/user constraints outrank interview answers and defaults.
2. Secrets are referenced by path only — never copied into the Plan, code,
   commits, or logs.
3. External (outside-the-workspace) actions are deny-by-default: only
   operations matching the Plan's allowlist — *(environment, resource type,
   name/prefix, allowed verbs)* — are permitted. An unlisted verb on a listed
   resource is denied. Every external-write policy the interview enables is
   compiled into allowlist entries; loop agents execute the allowlist, never
   infer authorization from policy prose.
4. Destruction is confined to the disposable workspace (container/sandbox).
   The one guarded exception: `delete-merged-feature-branch` when allowlisted
   (exact ref, verified merged, integration branch never deletable).

## Mechanical invariants

1. `docs/PLAN.md` is the stable entry point, forever. Restructure freely —
   the entry point holds and no information is lost.
2. The Plan persists the **full effective ruleset** (one line per rule,
   complete enough to act on). A fresh agent without this skill must be able
   to resume from the Plan alone.
3. Interview answers are persisted before any code work starts.
4. Ruleset changes pass adversarial review, land in the decision log as
   versioned entries, and are forbidden while any subgoal is `in-progress`.

Everything else — including the loop shape — is a default the interview can
override per project.
