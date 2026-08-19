# Bootstrap: interview + investigation → the Plan

Bootstrap is the one moment a human is present. **Ask now, so the nights never
have to.** Every question you leave unasked here becomes either a wrong guess
or an unnecessary stop at 3am. The interview is mandatory: never freeze policy
unilaterally when the human is one question away.

## Bootstrap sequence

1. **Recon (read-only).** Quick pass over the repo, its docs, spec/handoff
   files, CI config, and any sibling/convention repos you can see — so the
   interview presents discovered candidates ("I found `docs/client/handoff.md`
   — is that the contract?") instead of asking cold.
2. **Interview.** One topic at a time (A–J below). Policy questions present
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
   criteria (exact command + expected result each). Run the readiness
   contract's **content checks** on the candidate, then install
   `docs/PLAN.md` itself **last**. Add a one-line pointer to `docs/PLAN.md`
   from the repo's agent-instructions file (CLAUDE.md / AGENTS.md) if one
   exists.
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
  location (path only).
- **P:** Only the development environment is touchable. Everything not
  allowlisted — resource **or verb** — is prohibited, without interpretation.
  Credentials referenced by path only. Everything runs in containers; no
  installing dependencies on the host. Freedom inside the container — run,
  break, delete, experiment; the hard limit is the workspace boundary, and
  host files, mounted secrets, and shared services sit outside it even when
  reachable from inside.

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
- **P:** Short GitHub flow: integration branch → branch per subgoal →
  checkpoint commits → PR → CI green → merge → delete branch → re-branch.
  One branch = one subgoal, never mixed. Checkpoint commits small and
  frequent (message = which loop step completed) so a dead run recovers from
  the last checkpoint. Stacked branches only when subgoal N+1 needs unmerged
  code from N; max 2 levels; rebase onto integration when N merges;
  force-push only your own stack branches, never the integration branch.
  Auto-merge: CI green = merge, no human approval — a PR waiting overnight is
  a dead PR. Red CI: iterate with a NEW hypothesis each retry; out of
  hypotheses → park the subgoal (`blocked` + diagnosis) and return later in
  the session with a fresh subagent.

### I. Autonomy
- **F:** Project-specific additions to the stop-list, if any.
- **P:** **Decide → document → continue.** Stopping is the exception. Never
  stop for: style/naming/folder layout (convention repos decide); spec doubts
  with a reasonable interpretation (interpret, log in Inconsistencies,
  continue); failing tests or red CI (iterate); two viable options (pick the
  simpler, more reversible one, log it as "assumption to validate");
  information deducible by reading more (read more). Stop ONLY for the closed
  list: ① security — exposing secrets, permission changes, destructive or
  out-of-environment operations; ② outside scope or allowlist; ③ irreversible
  + indecidable from every source of truth. **Blocker scope:** a local
  blocker parks its subgoal (`blocked` + state, options, recommendation) and
  the run continues with the next executable subgoal; a global blocker
  (leaked secret, environment ambiguity, compromised CI, invalid allowlist,
  corrupt Plan) halts all mutation — diagnose and report. Before the session
  ends, revisit parked subgoals once with a fresh subagent. The morning
  report is always written (see loop-playbook.md).

### J. Loop shape & Plan properties
- **P:** The 8-step loop and Plan properties exactly as specified in
  loop-playbook.md and plan-template.md. The human may reshape any of it here
  — whatever is agreed becomes the Plan's ruleset, written in full.

## Readiness

Before declaring the Plan ready, run the readiness contract checklist in
plan-template.md. Any failure = not ready; fix, don't ship.
