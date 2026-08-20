# Multi-repo mode: hub and spokes

Applies when interview topic L declares multiple coordinated repos. The
failure this design kills: a central tracker "stale the moment a team moves".
The hub coordinates; it never tracks.

## The hub

One repo holds exactly what must be shared, nothing that any spoke owns:

- **Contracts** — shared interfaces. Machine-readable where more than one
  implementer consumes them: literal key/enum lists or schemas, never prose
  (prose independently rendered as `delivery` vs `delivery_mode` in the
  field). Contract changes land in the hub first; spokes never fork a
  contract locally.
- **Decision records (ADRs)** with a numbering registry: claim the number in
  the registry before creating the file; supersede, never delete.
- **The deliverable bar** — the externally-owned acceptance criteria (topic
  K; semantics and matrix per plan-template.md). Each spoke's coverage
  matrix maps the bar onto its own backlog, marking sibling-owned criteria
  `owned by <spoke>`.
- **The canonical protocol/skill copy** — the hub copy is canonical; spokes
  carry synced copies. A spoke detecting divergence runs ruleset-change
  intake (SKILL.md invariant 5) and raises its verdict through a hub channel
  (ADR proposal or inconsistency entry) so all spokes converge on ONE
  decision; local acceptance is interim, per non-blocking escalation.
- **Status feeds and digests** (below), plus templates for shared artifact
  types.

## Closed write channels

Spokes write to the hub ONLY through named PR channels — anything else is a
spoke-Plan matter. **Every channel a spoke enables is compiled into its
Plan's allowlist at interview (topic L)** — hub writes obey the same
deny-by-default floor as any external action; a channel missing from the
allowlist leaves a pending-escalation outbox item, never an inferred
permission. Per-channel hub merge policy: status → auto-merge on hub CI
green; inconsistency/ADR/contract → human-gated.

1. **Status** — one dated file per session at `status/<spoke>/<session>.md`
   (immutable per-session files, so parallel PRs never conflict at EOF),
   batch-merge exempt from the one-increment-per-PR rule (topic H). Pushing
   it happens immediately
   BEFORE the closing morning-report commit, and the report's last line
   records the status PR — the local report stays the spoke's final write.
   Reminders alone failed in the field (a spoke reached its 10th subgoal
   with central status still "No sessions yet").
2. **Inconsistency entry** — cross-repo contradictions, with the proposing
   spoke's interim resolution.
3. **ADR proposal.** Numbering: the claim is a one-line registry-only PR
   merged FIRST (the merge conflict is the lock); the ADR file PR references
   the merged claim. Protocol/skill-change proposals travel this channel too.
4. **Contract change.**

The hub repo runs this skill like any repo: its own Plan tracks hub curation
work (contracts, ADR registry, bar upkeep) — never spoke work.

Each spoke's `docs/PLAN.md` remains the only tracker of its work. The hub
never mirrors spoke subgoals.

## Escalation is non-blocking

Every escalation into a human-gated channel carries an **interim decision the
spoke proceeds on** ("keep building against contract v1 while proposing the
v2 field rename" is the model). Interim-proceed **never applies to stop-list
matters** — permission scope, credentials, destructive operations stop, full
stop. BRIEF re-checks pending escalations each session; a stale escalation is
re-raised in the status file, never silently dropped and never waited on.

## Parity protocol (sibling spokes)

- Reading siblings is encouraged; writing to them is forbidden.
- **Fetch the sibling's remote before any claim about its state** — both
  field teams misjudged each other from stale local checkouts and set
  conventions into a vacuum.
- Keep an **adoption ledger** in the spoke Plan's memory: sibling ideas as
  rows with adopted / not-yet status. Reading sibling code is also a defect
  source for your own (the field found a real bug in its own Dockerfile by
  diffing against the sibling's).
- At interview, assign a **convention-setter** per shared surface AND
  schedule an early parity-handshake subgoal — role assignment alone still
  allowed a seven-point convention divergence when both spokes scaffolded in
  parallel.
