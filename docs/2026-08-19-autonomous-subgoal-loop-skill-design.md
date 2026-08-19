# Design: `autonomous-subgoal-loop` skill

**Date:** 2026-08-19 (v2 — amended after Codex adversarial review round 1)
**Source:** `init-prompt-optimizado.md` (Spanish init prompt for the DRP backend autonomous agent)
**Status:** v1 approved by Mateo 2026-08-19 (interactive brainstorm). v2 amends it
per Codex review; the one change to an explicitly approved decision is the
**safety floor** (narrows "everything interviewable") — flagged for Mateo.

## Summary

A framework skill for plan-driven autonomous agent work on a project. One entry
point, two modes. Its central object is **the Plan** — a planning documentation
system under `docs/` in the *target* repo, entry point `docs/PLAN.md`. Agents
are disposable; the Plan is the persistent brain. Everything about how a given
project runs is decided in a bootstrap **interview** and persisted into the
Plan; the skill ships the source doc's ruleset as portable procedural defaults.

## Decisions (from brainstorm)

| Question | Decision |
|---|---|
| Lifecycle | One skill, mode by state: `docs/PLAN.md` ready → loop; absent → bootstrap; present-but-foreign/partial → repair |
| Inputs | Interview → persisted into the Plan itself. Loop mode needs zero inputs |
| Fixed vs configurable | Everything interviewable (framework) **except the safety floor and mechanical invariants below**; source ruleset = defaults |
| Call syntax | Bare invocation + optional free-text focus arg; reserved keyword `reconfigure` |
| Language | English body; Spanish original kept as reference |
| Name | `autonomous-subgoal-loop` |

## Invocation contract

- `/autonomous-subgoal-loop` — invoked in the target repo. **Target resolution:**
  the git root of the current working directory. Multi-Plan monorepos are out of
  scope v1; if the resolved root is ambiguous or surprising, bootstrap asks (a
  human is present at bootstrap), loop mode treats it as a global blocker.
- Mode dispatch:
  - No `docs/PLAN.md` at the root → **bootstrap mode**.
  - `docs/PLAN.md` present **and loop-ready** (it carries the ruleset section
    this skill writes) → **loop mode**.
  - `docs/PLAN.md` present but foreign, partial, or conflicted → **repair mode**:
    never execute subgoals from an unvalidated Plan; adopt/complete it
    interactively if a human is present, otherwise stop with a report.
  - Bootstrap writes `docs/PLAN.md` **last**, after its content is validated —
    a crashed bootstrap therefore never leaves a loop-ready-looking entry point.
- Optional free-text arg = session focus (e.g. `only subgoal 3`, `stop after two merges`).
- Reserved keyword **`reconfigure`**: re-opens the interview (whole or named
  section) even when the Plan exists. Ruleset changes: cannot touch the safety
  floor; are recorded as versioned decision-log entries; pass adversarial review
  before taking effect; apply from the next subgoal (an in-flight subgoal
  finishes under the old rules unless the change is safety-motivated).

## Safety floor (never interviewable, never reconfigurable)

1. **Explicit user/owner constraints outrank interview answers and defaults.**
2. **Secrets are referenced by path only** — never copied into the Plan, code,
   commits, or logs.
3. **External (outside-the-workspace) actions are deny-by-default.** Only
   operations matching the Plan's allowlist — entries of the form
   *(environment, resource type, name/prefix, allowed verbs)* — are permitted.
   An unlisted verb on a listed resource is still denied. Permission changes and
   destructive verbs never enter an allowlist by default.
4. **Destruction is confined to the disposable workspace** (the container/local
   sandbox). "Total local freedom" means inside that boundary only — not host
   files, mounted secrets, or shared services.

## Mechanical invariants (not interviewable)

1. **`docs/PLAN.md` is the stable entry point.** Restructuring is allowed
   anytime, provided the entry point holds and no information is lost.
2. **The Plan persists the full effective ruleset** — every rule in force, one
   line each, complete enough to act on. Never "defaults per skill X, plus
   deviations": a fresh agent without the skill installed must be able to
   resume from the Plan alone. The skill's playbook is the *text the interview
   copies and adapts from*, not a runtime dependency.
3. **Interview answers are persisted before any code work starts.**
4. **Ruleset changes pass adversarial review** and land in the decision log.

Everything else — including the loop shape — is a default the interview can
override.

## Bootstrap mode flow

1. **Recon (read-only):** quick pass over the repo, its docs, and any obvious
   spec/handoff files, so the interview can present discovered candidates
   instead of asking cold.
2. **Interview** — one topic at a time, each policy question presenting its
   default; accepting all defaults reproduces the source doc's *procedural*
   ruleset (facts are always project-specific and must be answered). Policies
   authorizing external writes (auto-merge, deploys, cloud resources) are
   confirmed explicitly — never silently bundled into "accept all defaults" —
   and auto-merge's prerequisites (CI exists and gates the integration branch)
   are verified, not assumed.
3. **Deep investigation** — each declared source of truth and convention repo
   (including how they organize docs). Answers are provisional until validated
   here; contradictions between answers and repo reality are resolved with the
   user or logged in Inconsistencies before the Plan is ready.
4. **Design the Plan system** — structure is the agent's decision, informed by
   investigation, passed through an **adversarial fresh-context subagent** with
   verdict obligation: can a truly fresh agent resume from this? Does it scale
   or become a monster file? Where will it rot?
5. **Write the Plan** — ruleset section, sources-of-truth table, scope boundary,
   verb-level allowlist, reading map, and an initial subgoal backlog with
   verifiable acceptance criteria. `docs/PLAN.md` itself is written last.
6. **Report** — what was decided, what was assumed ("assumption to validate"),
   what the first executable subgoal is.

## Interview schema (topics A–J)

**F** = fact, must be answered; **P** = policy, has a default.

| # | Topic | Asks for | Default (from source doc) |
|---|---|---|---|
| A | Mission | **F:** what the system is; what "done overall" looks like | — |
| B | Sources of truth | **F:** table of source → authority *domain* (the WHAT / the current HOW / conventions / historical-only) | **P:** conflict rule: cross-domain → that domain's authority wins; intra-domain or uncovered → log in Inconsistencies with proposed resolution, decide by general engineering criteria, continue without stopping. Docs have errors and bias: judge by internal + external consistency |
| C | Scope boundary | **F:** where our domain starts/ends; what we build; what lives outside; what to simulate and from which spec | **P:** simulate external inputs minimally; formats come from the spec source, never invented |
| D | Hard constraints | **F:** environments + which are touchable; allowlist as *(env, resource type, name/prefix, allowed verbs)*; credentials location | **P:** dev-only; everything not allowlisted (resource **or verb**) prohibited without interpretation; credentials referenced by path only; everything runs in containers; freedom inside the container, the hard limit is only outward |
| E | Code policy | — | **P:** no hardcoding, every parameter explicit; minimum necessary but correct and useful e2e; simple > complex; general > particular |
| F | Strategy | — | **P:** walking skeleton first (phase 0: full e2e piping with trivial logic), then real logic feature by feature |
| G | Testing | — | **P:** e2e first, several covering different edge cases; minimal unit/integration focused on edge cases, not coverage theater; local in container → push → CI; folder layout per convention repos |
| H | Git flow | **F:** integration branch name | **P:** short GitHub flow; one branch = one subgoal; small checkpoint commits (message = which loop step completed); stacking only when justified, max 2 levels; never force-push the integration branch; auto-merge on green CI, no human approval (explicit-confirm policy, prerequisites verified); red CI → iterate with a NEW hypothesis per retry, else park the subgoal and return later with a fresh subagent |
| I | Autonomy | **F:** any project-specific additions to the stop-list | **P:** decide → document → continue; never stop for style/naming/test-scope/resolvable ambiguity; closed stop-list: ① security/credentials/destructive or out-of-env ops, ② outside scope or allowlist, ③ irreversible + indecidable from any source of truth; **blocker scope**: local blocker → park subgoal + move on; global blocker (leaked secret, environment ambiguity, compromised CI, invalid allowlist, corrupt Plan) → halt all mutation, diagnose, report; before ending, revisit parked subgoals once with fresh eyes; **morning report always** — written incrementally via Plan updates so a dead run's report is reconstructed from checkpoints next session |
| J | Loop shape & Plan properties | — | **P:** the 8-step cycle below; fresh subagent per subgoal; Plan properties: cold onboarding; anti context-rot (pointers not copies; splitting a costly file is a signal, not an option); the Plan is general — never detailed design or code, and its reading map says what NOT to read; verifiable state (`pending | in-progress | done | blocked` + dependencies); system memory with required fields (see plan-template); lossless evolution |

## The default loop (topic J expanded)

One subgoal = one fresh-context subagent (implementer). Adversaries are
*separate* fresh-context subagents: they read only the artifact under review +
the acceptance criteria + the relevant source-of-truth excerpts — never the
implementer's reasoning. Verdict obligation: concrete findings, or an explicit
list of what was verified and why it passes; "looks fine" is not a verdict;
unresolved findings block advancement. If subagent isolation is unavailable,
degrade explicitly: sequential fresh-eyes pass (re-read only from files, not
from conversation memory) and note the limitation in the log.

```
1. BRIEF      → fresh implementer reads docs/PLAN.md → its subgoal's read list
               (only that). Write-ahead intent as PREDICTION: "attempting X,
               expect Y" — this is what makes surprise measurable.
2. PLAN       → small steps; acceptance criteria + NAMED test cases (inputs,
               expected outcomes) fixed HERE, before implementation.
               ADVERSARIAL GATE #1: fresh reviewer attacks the subgoal plan.
3. EXECUTE    → minimum necessary, explicit, no hardcoding.
4. ADVERSARY  → ADVERSARIAL GATE #2: fresh reviewer attacks the diff (logic,
               edge cases, consistency with spec + conventions, hardcoding).
5. TEST       → run the tests named at step 2 (plus suite) in the container;
               retest anything old you touched. Modifying an existing test
               requires a logged justification — tests are not "fixed" to pass.
6. CLEAN      → parsimonious refactor: dead code, orphan helpers, temp samples,
               ownerless TODOs. Leave the campsite cleaner.
7. REFLECT    → 3–6 lines: what surprised me (observation the Plan didn't
               predict)? Every surprise states its PROPAGATION — which Plan
               sections/subgoals it invalidates; the next subgoal's BRIEF
               verifies it. RECURRENCE RULE: the same surprise twice = model
               error → restructure the Plan / distrust the source, don't log
               a third entry.
8. UPDATE     → `done` ONLY with evidence executed this session (verification
               command + result referenced in the Plan). Update state,
               decisions, problems; merge; clean branch.
```

**Concurrency assumption:** one autonomous session at a time (per source doc;
worktrees/parallel agents out of scope v1 — stated in SKILL.md). A fresh session
finding a stale `in-progress` subgoal with no live run treats it as a crashed
run: recover from the write-ahead intent + checkpoints, don't restart blind.

## Loop mode flow

Read `docs/PLAN.md` (validate loop-ready) → if the last run died mid-way,
reconstruct its morning report from checkpoints → pick next executable subgoal
(**selection rule:** first `pending` whose dependencies are all `done`, in
backlog order; `blocked` requires new information to re-enter) → run the cycle
→ repeat until no executable subgoal remains or the session-focus arg says stop
→ revisit parked subgoals once with a fresh subagent → write the morning
report (merged, blocked+why, decisions & assumptions-to-validate, refactors,
new tests, recommended next attack).

## Skill file layout

```
autonomous-subgoal-loop-skill/
  SKILL.md                 # frontmatter, dispatch, safety floor, invariants, call syntax (lean)
  references/
    interview.md           # full interview schema + defaults (topics A–J)
    loop-playbook.md       # default loop + autonomy + git flow, full text the interview adapts
    plan-template.md       # Plan properties + required record fields + compact-ruleset format
```

`plan-template.md` carries required fields: subgoal (id, objective 1–2 lines,
read-list, acceptance criteria, status, dependencies), decision log (date,
decision, why, discarded alternative — one line; includes assumptions to
validate), lessons/surprises (append-only: expectation vs observation vs
propagation), inconsistencies (source, description, proposed resolution,
status), open problems, reading map (paths + what NOT to read; credentials
path only).

Frontmatter description (triggering conditions only, per writing-skills SDO):
*"Use when starting or resuming autonomous agent work on a project —
overnight/unattended runs, plan-driven multi-session development, bootstrapping
a docs/PLAN.md planning system, or executing subgoals from an existing Plan."*

Deployment: copy `autonomous-subgoal-loop-skill/` →
`~/.claude-cura/skills/autonomous-subgoal-loop/` (repo convention).

## Testing plan (writing-skills TDD)

Five scenario families, baseline (RED) before the skill exists, then with the
skill (GREEN), in a mock target repo. Baseline behavior is *observed and
documented verbatim*, not assumed.

1. **Bootstrap:** mock repo + "set up autonomous overnight work".
2. **Cold resume:** fresh agent + the produced Plan only — full rule
   compliance, not merely identifying the next subgoal. Variant: stale
   `in-progress` from a crashed run.
3. **Discipline under pressure:** done-without-evidence temptation; adversary
   "looks fine" temptation. Multiple reps (single samples lie).
4. **Dispatch edge cases:** foreign/partial `docs/PLAN.md` → must route to
   repair, not loop.
5. **Safety-floor override attempt:** interview answers try to allowlist a
   production resource / relax secret handling → skill must refuse and record.

REFACTOR: capture rationalizations verbatim, add counters, re-test.

## Appendix: Codex review round 1 — disposition

Verdict was REWORK (18 findings). Dispositions:

| # | Finding (short) | Disposition |
|---|---|---|
| 1 | Invariant core permits unsafe ruleset | **Adapted**: safety floor added (secrets, deny-by-default external actions, destruction boundary, user constraints outrank). Evidence-backed `done` stays a default, not an invariant — quality discipline, not safety; projects may legitimately run lighter loops |
| 2 | Allowlist loses verb restrictions | **Accepted**: allowlist = (env, type, name/prefix, verbs) |
| 3 | "Plan alone" vs "defaults live in skill" | **Accepted**: Plan persists full effective ruleset; playbook is copy-source, not dependency |
| 4 | File existence invalid discriminator | **Adapted**: loop-ready check (ruleset section present) + repair mode + write-entry-point-last; no schema_version machinery |
| 5 | Target resolution undefined | **Adapted**: git root of cwd; monorepo multi-Plan out of scope v1 |
| 6 | No leases/CAS for concurrency | **Rejected as scoped**: source explicitly scopes to one agent at a time; documented assumption + stale in-progress recovery instead. Leases/CAS is infrastructure, not prose-skill material |
| 7 | Adversarial review weakened | **Accepted**: two gates (plan, diff) + verdict schema + findings block |
| 8 | Fresh-context mechanism/fallback | **Adapted**: roles + brief contents specified; sequential fresh-eyes fallback with logged limitation (blocking execution outright is disproportionate) |
| 9 | Dangerous defaults w/o validation | **Adapted**: external-write policies are explicit-confirm at interview; auto-merge prerequisites verified; local freedom = container only |
| 10 | Global vs local blockers | **Accepted** |
| 11 | Facts frozen before investigation | **Accepted**: recon → interview → investigate → validate |
| 12 | "Defaults reproduce source" false | **Accepted**: claim narrowed to procedural defaults |
| 13 | Tests retrofittable | **Accepted**: named test cases at PLAN step |
| 14 | Selection/termination not computable | **Adapted**: dependencies + deterministic selection rule; no lease machinery |
| 15 | Report can't survive dead run | **Accepted**: incremental checkpoints + reconstruction |
| 16 | Memory schemas weakened | **Accepted**: required fields in plan-template.md + Plan-is-general boundary + do-not-read map |
| 17 | Reconfigure unsafe | **Adapted**: can't touch safety floor; versioned + adversarial review + next-subgoal retroactivity. Full transaction protocol rejected as disproportionate |
| 18 | Testing plan gaps | **Adapted**: +2 families (dispatch edges, safety override), multi-rep discipline, observed-not-assumed baselines. Full crash-injection matrix rejected as disproportionate for a prose skill |
