# Loop mode: executing subgoals

This is the default playbook. The Plan's ruleset is authoritative — where the
project's interview changed a rule, the Plan wins. Read the Plan's ruleset
first and follow *it*, using this file for the mechanics it doesn't restate.

## Session flow

1. Minimal integrity preflight, read-only: `docs/PLAN.md` exists, marker
   first line, no conflict markers/truncation. Failure → repair mode.
2. Open THIS session's record (id, date, focus, `running`) AND its reports-
   index row **in one commit**, before any other write — it's what makes
   this run's own death detectable. (If Plan integrity forbade the write,
   record out-of-band and stay in repair.)
3. Skill-stamp check (SKILL.md invariant 5): recompute the stamp per
   plan-template.md. On divergence with no recorded verdict for the loaded
   version: first recover or park any crashed `in-progress` subgoal under
   its original ruleset. **Unattended, the intake never self-approves**: log
   the proposal (intake record), continue the whole session on the stamped
   ruleset, and leave adoption to an attended `reconfigure`. The one
   exception is a floor-tightening that is a mechanical strict superset of
   the old floor (logged as such); a reworded or removed floor line is not a
   tightening — a loosened floor is a **global blocker**.
4. Dead-run pass: any OTHER session record still `running` with no closing
   report — regardless of subgoal states — is a dead run: reconstruct its
   report from step journals, checkpoints, git/PR state, and test evidence.
5. Full readiness contract + the reading map's environment smoke commands.
   Smoke commands are **read-only existence/reachability checks by
   definition** — a mutating smoke command is a malformed Plan (repair).
   Readiness failure → repair. A failed smoke on credentials, target
   identity, or a touchable-environment fact = **global blocker**; missing
   optional information (an unreachable sibling) = local, logged.
6. If subgoal zero sits `in-progress` from bootstrap, close it first — its
   closure is a record update, not a loop run: fill its evidence with the
   now-observed bootstrap-merge SHA (its design review already fills both
   review slots) and set `done`. Then pick the next executable subgoal:
   first `pending` whose dependencies are all `done`, in backlog order;
   recompute the Plan's next-action record with every state change
   (plan-template.md). During normal selection,
   `blocked` re-enters only with new information; the one exception is step
   8's end-of-session fresh-eyes revisit, which needs none. Session-focus
   argument narrows this selection.
7. Run the loop below — one fresh-context subagent per **attempt** (a
   revisited subgoal gets a new fresh subagent, never the old context).
8. Repeat until no executable subgoal remains (or the focus says stop). Then
   revisit parked subgoals once with a fresh subagent — fresh eyes on a
   parked problem beat attempt 15 from the same context. Record the revisit
   as a line in this session's record, so it's attributable to this session.
9. Write the morning report, closing the session record.

## Driving a whole night with /goal

On runtimes with a goal command (Claude Code's `/goal`), start unattended
sessions with the skill invocation plus a completion condition, so the session
keeps working until the night is actually done. The condition must be a
**pointer to Plan state, never a restatement of the backlog** (conditions cap
at 4,000 characters — and a backlog copy would rot by the second subgoal):

```
/goal this session has terminated per its Plan's ruleset: its session record
is closed by its morning report (or an out-of-band report exists, if a
Plan-integrity blocker forbade Plan writes), and no work the session's focus
and ruleset still allow remains executable
```

The condition targets the session-terminal state — the closed session record —
not individual obligations: focus-stops, blocker terminations, and
pending-behind-blocked subgoals are all legitimate endings the report
captures, and nothing may continue past the morning report (the run's last
write). Keep any condition you write or recommend well under the
4,000-character cap; if it doesn't fit comfortably, it's restating state that
belongs in the Plan.

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

## The architecture is not written in stone

The planned implementation approach is a model, not a contract. An implementer
who finds a better way that serves the same objective proposes it rather than
silently complying or silently deviating: persist the proposal (the better
way; why it aligns with the objective and constraints; what it invalidates)
and talk it out with a fresh adversary (gate-1 rules: verdict obligation).

**Scope of this channel: implementation approach only.** Changing acceptance
criteria, test cases, or verification commands uses their own path (logged
justification + renewed gate 1). Changing ruleset, scope, objectives, or
allowlist goes through `reconfigure` — park or finish the subgoal first.
Safety floor and owner constraints are outside every channel.

- **Agreement** → one decision-log entry (old approach, new approach, why,
  discarded alternative); update the execution plan; then a fresh gate-1
  review of the updated plan — final artifact only, no negotiation
  transcript — before execution.
- **No agreement** → implement as planned ONLY if the original plan still
  stands gate-1-approved and the adversary records the proposal as an
  optional improvement; park the proposal in Open Problems for the morning.
  An unresolved correctness or constraint finding against the original plan
  still blocks — a disagreement of taste is not a finding, and a finding is
  not taste.

Never silent deviation, never implement-and-keep-debating.

## The loop (per subgoal)

```
1. BRIEF      Fresh implementer reads docs/PLAN.md: state, lessons flagged for
              this subgoal, its read list (ONLY that). Before touching code,
              write-ahead the intent as a PREDICTION in the Plan:
              "in-progress: attempting X, expect Y" — committed as its own
              dedicated commit ending this step (the cleanest crash-recovery
              artifact a run leaves). Plan-state writes — write-ahead, step
              journal, session records — land on the INTEGRATION branch;
              only code rides the feature branch, so a deleted or unmerged
              branch never strands the Plan's memory of it. If the branch
              batches subgoals into one coherent increment, the
              justification lives here, and the batched subgoals close
              together at the increment's merge — evidence per subgoal, all
              referencing that one merge SHA; within the increment, a
              dependency counts as satisfied once its gate 2 passes. A dead run's successor reads
              what was being attempted; a live run measures surprise against
              it.
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
              Findings are fixed before advancing. Record in the subgoal's
              diff-review slot: verdict, findings count, and the reviewed
              range as `base_sha..head_sha` (the pre-adversary checkpoint is
              the free base). If any later step changes the code (test
              fixes, cleanup), the review is stale: repeat gate 2 on the new
              diff — the recorded range must end at the commit that actually
              merges.
5. TEST       Run the tests fixed at PLAN (plus the suite) in the container.
              Touched something old? Re-test it. Modifying an existing test
              requires a justification in the decision log — a test is
              evidence, not an obstacle. Tests must BIND: ask what a broken
              implementation would have to do to still pass; observe side
              effects (logs, retries, cleanup) directly; measure budgeted
              metrics on the exact span the budget names. For side-effect
              deliverables, mutation is the honest instrument — delete the
              feature; a suite that stays green was documentation. COMMIT
              BEFORE ANY DESTRUCTIVE VERIFICATION (mutation runs, checkouts,
              resets): uncommitted fixes are indistinguishable from the
              mutations you're about to revert.
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
              only then set `done`. The status transition and its evidence
              land in the SAME commit, and evidence is written from the
              result, never in anticipation of one. Closing PRESERVES the
              write-ahead prediction: add the delivered note beside it (never
              overwrite it) — REFLECT reads the delivered-vs-attempted delta.
              Post-merge findings never reopen `done`: they spawn a suffixed
              follow-up subgoal. A crash can leave an unmerged subgoal
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
flow step 4) — which works because the step journal and checkpoints were
written along the way.

**Global blocker paths.** A global blocker halts code and external mutation —
including the multi-repo hub status push, which is deferred like any external
write (the report notes the pending append). The Plan report is still written
— that's the diagnosis the morning needs — UNLESS the Plan's own integrity is
the blocker (corruption, suspected tampering): then report out-of-band (final
message / a separate file outside `docs/`) and state explicitly that the Plan
was not touched.
