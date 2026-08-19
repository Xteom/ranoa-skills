# Loop mode: executing subgoals

This is the default playbook. The Plan's ruleset is authoritative — where the
project's interview changed a rule, the Plan wins. Read the Plan's ruleset
first and follow *it*, using this file for the mechanics it doesn't restate.

## Session flow

1. Validate `docs/PLAN.md` against the readiness contract (plan-template.md).
   Failure → repair mode, not execution.
2. If the previous run died mid-way (stale `in-progress`, no morning report):
   reconstruct its report from the step journal, checkpoints, git/PR state,
   and test evidence; recover the subgoal from its write-ahead intent.
3. Pick the next executable subgoal: first `pending` whose dependencies are
   all `done`, in backlog order. `blocked` re-enters only with new
   information. Session-focus argument narrows this selection.
4. Run the loop below — one fresh-context subagent per subgoal.
5. Repeat until no executable subgoal remains (or the focus says stop). Then
   revisit parked subgoals once with a fresh subagent — fresh eyes on a
   parked problem beat attempt 15 from the same context.
6. Write the morning report.

## Fresh context is mechanism, not metaphor

Each subgoal starts in a new subagent/session that reads only its brief: the
Plan's entry point → its subgoal's read list, nothing else. Double benefit:
zero context rot, and the Plan is validated every iteration — a fresh agent
that can't resume means the Plan failed, detected early.

Adversaries are *separate* fresh-context subagents. Reviewer brief: the
artifact under review (subgoal plan or diff) + acceptance criteria + relevant
source-of-truth excerpts. Never the implementer's reasoning. **Verdict
obligation:** concrete findings, or an explicit list of what was verified and
why it passes. "Looks fine" is not a verdict. Unresolved findings block
advancement.

If subagent isolation is unavailable in this runtime, degrade explicitly:
sequential fresh-eyes pass — re-read only from files, not conversation memory
— and note the limitation in the log.

## The loop (per subgoal)

```
1. BRIEF      Fresh implementer reads docs/PLAN.md: state, lessons flagged for
              this subgoal, its read list (ONLY that). Before touching code,
              write-ahead the intent as a PREDICTION in the Plan:
              "in-progress: attempting X, expect Y." A dead run's successor
              reads what was being attempted; a live run measures surprise
              against it.
2. PLAN       Small steps. Fix HERE, before implementing: named test cases
              (inputs, expected outcomes) AND the exact verification command +
              expected result. Changing any of these later = logged
              justification + renewed plan review. Use the runtime's process
              skills (brainstorming, TDD) when available.
              ADVERSARIAL GATE 1: fresh reviewer attacks the subgoal plan.
3. EXECUTE    Minimum necessary. Explicit parameters, no magic values.
4. ADVERSARY  ADVERSARIAL GATE 2: fresh reviewer attacks the diff — logic,
              edge cases, consistency with spec and conventions, hardcoding.
              Findings are fixed before advancing.
5. TEST       Run the tests fixed at PLAN (plus the suite) in the container.
              Touched something old? Re-test it. Modifying an existing test
              requires a justification in the decision log — a test is
              evidence, not an obstacle.
6. CLEAN      Parsimonious refactor before closing: dead code, orphan
              helpers, temporary samples, ownerless TODOs, unused logic
              branches. Leave the campsite cleaner than you found it.
7. REFLECT    3–6 lines: what did I learn — and what SURPRISED me (an
              observation the Plan didn't predict)? Every surprise states its
              PROPAGATION: which Plan sections/subgoals it invalidates; the
              next subgoal's BRIEF verifies it. Recurrence: the same surprise
              twice = the model is wrong, not the world — increment/link the
              existing entry, open an Inconsistencies item, and route the
              model change (restructure, source-authority doubt) through the
              decision log. Recorded, never silent.
8. UPDATE     `done` ONLY with evidence executed this session: the
              verification command fixed at PLAN ran, and its result is
              referenced in the Plan. If that command cannot run here, the
              subgoal is `blocked` with a diagnosis — the criterion is never
              silently downgraded to whatever was runnable. Update state,
              decisions, problems; restructure the Plan if needed (with
              adversary). Merge; clean branch (guarded allowlist operation).
```

**Step journal:** after each completed step, append one compact line to the
subgoal's entry — step, key outcome, command/result if any. With checkpoint
commits, this is what makes a mid-loop crash recoverable and the morning
report reconstructable.

**Checkpoint commits are the autonomy mechanism, not politeness.** Commit
small and frequent on the subgoal branch (message = loop step completed).
Work left uncommitted "for morning review" is work lost to the next fresh
agent — there is no morning reviewer; the morning reads the Plan and the
merged history.

## Autonomy rules (nocturnal default)

**Decide → document → continue.** Full rules live in the Plan's ruleset
(interview topic I): never-stop list, the closed 3-item stop list, local vs
global blocker handling. Ambiguity → the simplest, most reversible option,
logged as "assumption to validate", and keep moving. A documented reversible
assumption costs minutes tomorrow; a stopped night costs the night.

## Morning report (always — the run's last write)

What merged; what's `blocked` and why; decisions taken and assumptions to
validate; refactors/cleanups; new tests; recommended next attack. It's the
first thing read in the morning; without it, auditing the run costs more than
supervising it would have. If the run dies before writing it, the next
session reconstructs it (session flow step 2) — which works because the step
journal and checkpoints were written along the way.
