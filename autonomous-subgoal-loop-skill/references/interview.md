# Bootstrap: interview + investigation → the Plan

Bootstrap is normally the one moment a human is present. **Ask now, so the
nights never have to.** Every question you leave unasked here becomes either a
wrong guess or an unnecessary stop at 3am. Never freeze policy unilaterally
when the human is one question away.

**Seeded bootstrap (the one unattended exception).** If the repo carries a
seed facts-pack — a kickoff/handoff file that pre-answers the interview
(mission, sources, scope, constraints, policies) — bootstrap may run
unattended from it, under these conditions:

- The seed answers every fact topic **explicitly, including the yes/no ones**
  — I additions ("none"), K ("no external bar" or the bar), L ("single
  repo" or the repo set). A one-word answer costs the seed author nothing; an
  omission silently drops stop conditions or delivery obligations, so any
  silence is a gap.
- Ordinary external-write policies are enabled only where the seed authorizes
  them explicitly. **Destructive and permission-changing verbs are never
  seed-grantable**: the seed may propose them, and they stay out of the
  allowlist until a live human confirms (safety floor #3).
- Every seed-derived answer is logged "answered by seed <path>", and the
  decision log records the seed's commit hash and author. Authorship is
  established **mechanically**: the seed is referenced by path from the
  repo's human-maintained agent-instructions file (CLAUDE.md / AGENTS.md),
  or its commit author is named there — a merely-committed seed satisfying
  neither is treated as gap-everywhere (anyone with write access can commit
  a file; that is not a handoff).
- The consumed seed gets its lifecycle line: `one-time, executed <date>`.

Gaps: interview the human if present. Unattended, a gap on a substantive
fact topic is a **hard stop** — facts are never guessed: commit a
`BOOTSTRAP-BLOCKED.md` naming the missing topics and stop with a report
(likewise when no seed exists at all). Committing and pushing that beacon is
the safety floor's sole pre-Plan exception (SKILL.md floor #3) — a docs-only
commit to the integration branch, because an unpushed beacon in an ephemeral
sandbox reaches no one. When a policy's verb wasn't confirmed (no live human), the
compiled ruleset line **omits that verb** and notes it pending confirmation
— the topic-H flow compiles as "merge → log cleanup-pending → re-branch"
rather than instructing a denied delete. A seed should be topic-keyed so
coverage is checkable, and the adversarial design review (step 4) includes a
seed-coverage verdict. **Attended bootstrap with a seed is a fast-path
confirmation, not silence:** present the seed's answers — external-write
policies item by item — for one-shot confirmation. A seed is a pre-paid
interview, not a bypass of it.

## Bootstrap sequence

1. **Recon (read-only).** Quick pass over the repo, its docs, spec/handoff
   files, CI config, and any sibling/convention repos you can see — so the
   interview presents discovered candidates ("I found `docs/client/handoff.md`
   — is that the contract?") instead of asking cold.
2. **Interview.** One topic at a time — A–I, then K, L, then J last. Policy questions present
   their default; accepting all defaults reproduces this skill's *procedural*
   ruleset — facts are always project-specific and must be answered. Policies
   that authorize external writes (auto-merge, deploys, cloud resources,
   branch cleanup) are confirmed explicitly, never bundled silently into
   "accept all defaults"; verify auto-merge's prerequisite (CI exists and
   gates the integration branch) rather than assuming it.
3. **Deep investigation.** Read each declared source of truth and convention
   repo (including how they organize their docs). Interview answers are
   provisional until validated here; a contradiction between an answer and
   repo reality goes back to the human now, or into Inconsistencies with a
   proposed resolution.
4. **Design the Plan system.** The structure is YOURS to design — one file
   today, an index of files when growth demands it. Optimize for the next
   fresh agent's read. Then pass the design through an adversarial
   fresh-context subagent (verdict obligation, see loop-playbook.md): can a
   truly fresh agent resume from this? Does it scale or become a monster
   file? Where will it rot?
5. **Write the Plan.** Everything in plan-template.md: marker line, mission,
   ruleset (complete per the completeness contract), sources of truth, scope,
   allowlist (compiled from the confirmed policies), reading map, memory
   sections, and an initial subgoal backlog with verifiable acceptance
   criteria (exact command + expected result each).
   - **The Plan reaches the integration branch before any code branch is
     cut.**
   - **Subgoal zero:** the bootstrap records itself as a subgoal, installed
     as `in-progress` with its write-ahead — evidence citing its own merge
     SHA cannot exist before the merge does. The first loop session closes
     it (session flow step 6) with the *observed* bootstrap-merge SHA; the
     step-4 design review fills gate 1, and gate 2 runs retrospectively at
     that closure — a fresh reviewer over the actual bootstrap increment
     (`base..merge`, Plan + wiring); findings spawn follow-up subgoals,
     they never reopen the install.
   - A merge that predates CI (nothing to be green yet) uses a one-time
     merge-without-ci allowance the human or seed authorized.
   - **Install atomically:** run the readiness contract's content checks on
     the candidate, then land ONE bootstrap increment — a single PR/merge
     carrying `docs/PLAN.md` (written last within it) together with the
     entry-point wiring (agent-file pointer + portable session prompt +
     lifecycle lines, per plan-template.md "Entry-point wiring"). The
     bootstrap PR is also the landing path for root-level wiring files,
     since `push-plan-state` covers `docs/**` only. A crash never leaves
     wiring without a Plan or a Plan without wiring.
6. **Report.** What was decided; every assumption marked "assumption to
   validate"; the first executable subgoal.

## Interview topics

**F** = fact (no default, must be answered) · **P** = policy (default below;
human can override any of it)

### A. Mission
- **F:** What is the system being built? What does "done overall" look like?

### B. Sources of truth
- **F:** Table of source → authority **domain**. No global ranking — each
  source is the authority in its domain and doesn't compete outside it.
  Typical domains: the WHAT (client contract/spec), the current HOW (existing
  implementation), CONVENTIONS (sibling repos: patterns, CI/CD, branch/test
  layout), historical-only (authoritative over nothing).
- **P (conflict rule):** Cross-domain clash → that domain's authority wins.
  Intra-domain clash or uncovered case → log in Inconsistencies with a
  proposed resolution, decide by general engineering judgment (internal
  consistency: sound logic and practices; external consistency: correct from
  the consumer's point of view), and continue without stopping. Documents
  have errors and bias — authority is per-domain, not infallibility.

### C. Scope boundary
- **F:** Where does our domain start and end? What do we build; what lives
  outside (other teams); what external inputs do we simulate?
- **P:** Simulate external inputs minimally — a small sample imitating each
  input plus an example trigger/spec. Their formats come from the spec
  source, never invented.

### D. Hard constraints
- **F:** Environments and which are touchable. External allowlist as
  *(environment, resource type, name/prefix, allowed verbs)*. Credentials
  location (path only). A machine-local path map: shared docs use
  repo-relative or explicitly machine-scoped paths, and each environment fact
  gets a smoke command (credentials file exists, sibling repos reachable)
  that sessions can run at start — documented worlds and real machines
  diverge.
- **P (overridable defaults):** only the development environment is
  touchable; everything runs in containers; no installing dependencies on
  the host; freedom to experiment inside the container. *(The safety floor —
  SKILL.md — also binds here: deny-by-default allowlist, path-only
  credentials, workspace-confined destruction. It is never overridable and
  is deliberately not restated in this overridable block.)*

### E. Code policy
- **P:** No magic values; every parameter passed explicitly (a default that
  exists is a default that's passed explicitly). Minimum necessary but
  correct and useful end-to-end. When in doubt between simple and complex,
  simple. General > particular: code should survive future modification.

### F. Strategy
- **P:** Walking skeleton first — phase 0 is piping only: the full flow runs
  end-to-end on sample data with trivial logic, proving everything connects
  and is testable. Then replace trivial logic with real logic feature by
  feature, each small but useful.

### G. Testing
- **P:** e2e first: several, covering different edge cases, replicating the
  full flow including modifications. Unit/integration: the minimum that
  proves behavior, focused on edge cases — not coverage theater. Flow: test
  locally in the container → push → CI. Folder layout per the convention
  repos.

### H. Git flow
- **F:** Integration branch name.
- **P:** Short GitHub flow: integration branch → branch per increment →
  checkpoint commits → PR → CI green → merge → delete branch → re-branch.
  **One branch = one coherent increment** — usually one subgoal; batching
  tightly-coupled subgoals is allowed when the write-ahead records the
  justification. Unrelated subgoals never mix. Thread the subgoal id through
  branch (`sg-<id>-<slug>`), commit prefixes, and PR title, so one grep
  reconstructs a subgoal's lifecycle. Checkpoint commits small and frequent
  (message = which loop step completed) so a dead run recovers from the last
  checkpoint. Stacked branches only when subgoal N+1 needs unmerged
  code from N; max 2 levels; rebase onto integration when N merges;
  force-push only your own stack branches, never the integration branch.
  Auto-merge: CI green = merge, no human approval — a PR waiting overnight is
  a dead PR. The PR is created (or auto-merge armed) only AFTER the
  diff-review slot is filled with no unresolved findings — an armed PR is a
  merge decision, and unreviewed code must not be able to land by CI timing. Red CI: iterate with a NEW hypothesis each retry, within a
  retry budget (default: 5 attempts per subgoal per session — interviewable);
  out of hypotheses or budget → park the subgoal (`blocked` + diagnosis,
  attempts recorded) and return later in the session with a fresh subagent.

### I. Autonomy
- **F:** Project-specific additions to the stop-list, if any.
- **P:** **Decide → document → continue.** Stopping is the exception. Never
  stop for: style/naming/folder layout (convention repos decide); spec doubts
  with a reasonable interpretation (interpret, log in Inconsistencies,
  continue); failing tests or red CI (iterate); two viable options (pick the
  simpler, more reversible one, log it as "assumption to validate");
  information deducible by reading more (read more). Stop ONLY for the closed
  list: ① security — exposing secrets, permission changes, or destructive /
  out-of-environment operations that are NOT explicitly allowlisted (a
  confirmed guarded verb whose preflight passes proceeds; it was already
  human-approved); ② outside scope or allowlist; ③ irreversible +
  indecidable from every source of truth. **Blocker scope:** a local
  blocker parks its subgoal (`blocked` with plan-template.md's required
  fields) and the run continues with the next executable subgoal; a global
  blocker
  (leaked secret, environment ambiguity, compromised CI, invalid allowlist,
  corrupt Plan) halts all mutation — diagnose and report. Before the session
  ends, revisit parked subgoals once with a fresh subagent. The morning
  report is always written (see loop-playbook.md).

### K. External acceptance bar
- **F:** Are any acceptance criteria imposed from outside the Plan (a client
  milestone bar, a contract, a parity requirement)? If yes, record the bar's
  source + revision and maintain the coverage matrix per plan-template.md —
  criteria owned by no subgoal are how milestones fail silently.

### L. Multi-repo coordination
- **F:** Does the project span multiple coordinated repos? If yes, read
  `references/multi-repo.md` and interview its topics (hub, write channels,
  parity roles).

### J. Loop shape & Plan properties
- **P:** The 8-step loop and Plan properties exactly as specified in
  loop-playbook.md and plan-template.md. The human may reshape any of it here
  — whatever is agreed becomes the Plan's ruleset, written in full.

## Readiness

Before declaring the Plan ready, run the readiness contract checklist in
plan-template.md. Any failure = not ready; fix, don't ship.
