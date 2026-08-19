# Loop mode: executing subgoals

This is the default playbook. The Plan's ruleset is authoritative — where the
project's interview changed a rule, the Plan wins. Read the Plan's ruleset
first and follow *it*, using this file for the mechanics it doesn't restate.

## Session flow

1. Validate `docs/PLAN.md` against the readiness contract (plan-template.md).
   Failure → repair mode, not execution.
2. If any session record is still `running` with no closing morning report —
   regardless of subgoal states — that run died: reconstruct its report from
   step journals, checkpoints, git/PR state, and test evidence; recover any
   `in-progress` subgoal from its write-ahead intent.
3. Open THIS session's record (id, date, focus, `running`) before anything
   else — it's what makes this run's own death detectable.
4. Pick the next executable subgoal: first `pending` whose dependencies are
   all `done`, in backlog order. During normal selection, `blocked` re-enters
   only with new information; the one exception is step 6's end-of-session
   fresh-eyes revisit, which needs none. Session-focus argument narrows this
   selection.
5. Run the loop below — one fresh-context subagent per **attempt** (a
   revisited subgoal gets a new fresh subagent, never the old context).
6. Repeat until no executable subgoal remains (or the focus says stop). Then
   revisit parked subgoals once with a fresh subagent — fresh eyes on a
   parked problem beat attempt 15 from the same context.
7. Write the morning report, closing the session record.

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
2. PLAN       Small steps, written as the subgoal's execution-plan artifact
              (bounded; stored where the Plan's structure puts it; referenced
              from the subgoal record — this is what the reviewer receives
              and what a crash can't lose). Fix HERE, before implementing:
              named test cases (inputs, expected outcomes) AND the exact
              verification command + expected result. Changing any of these
              later = logged justification + renewed plan review. Use the
              runtime's process skills in order — brainstorming → planning →
              TDD — where available; the loop supplies the discipline for
              whichever is missing.
              ADVERSARIAL GATE 1: fresh reviewer attacks the execution plan.
              Record verdict + findings→resolutions (or the explicit verified
              list) in the subgoal's plan-review slot.
3. EXECUTE    Minimum necessary. Explicit parameters, no magic values.
4. ADVERSARY  ADVERSARIAL GATE 2: fresh reviewer attacks the diff — logic,
              edge cases, consistency with spec and conventions, hardcoding.
              Findings are fixed before advancing. Record verdict + reviewed
              branch/commit in the subgoal's diff-review slot.
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
8. UPDATE     Merge first (per the git policy), then close: fill the
              subgoal's evidence slot — date, the verification command fixed
              at PLAN as actually run, its actual result, merge SHA/PR — and
              only then set `done`. A crash can leave an unmerged subgoal
              `in-progress`; it can never leave `done` pointing at unmerged
              code. If the verification command cannot run here, the subgoal
              is `blocked` with its required fields (diagnosis, state,
              hypotheses tried, options, recommendation, scope) — the
              criterion is never silently downgraded to whatever was
              runnable. Update decisions and problems; restructure the Plan
              if needed (with adversary); clean the branch (guarded allowlist
              operation); archive the execution-plan artifact.
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
validate; refactors/cleanups; new tests; recommended next attack. It closes
the session record opened at start. It's the first thing read in the morning;
without it, auditing the run costs more than supervising it would have. If
the run dies before writing it, the next session reconstructs it (session
flow step 2) — which works because the step journal and checkpoints were
written along the way.

**Global blocker paths.** A global blocker halts code and external mutation.
The Plan report is still written — that's the diagnosis the morning needs —
UNLESS the Plan's own integrity is the blocker (corruption, suspected
tampering): then report out-of-band (final message / a separate file outside
`docs/`) and state explicitly that the Plan was not touched.
