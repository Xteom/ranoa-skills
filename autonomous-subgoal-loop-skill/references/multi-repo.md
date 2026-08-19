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
  K). The bar defines what done and parity mean, not how or in what order a
  spoke gets there. Each spoke's coverage matrix maps the bar onto its own
  backlog.
- **The canonical protocol/skill copy** (spokes carry synced copies; a
  divergence is ruleset-change intake per SKILL.md invariant 5, in every
  repo).
- **Status feeds and digests** (below), plus templates for shared artifact
  types.

## Closed write channels

Spokes write to the hub ONLY through named PR channels — anything else is a
spoke-Plan matter:

1. **Status append** — one dated paragraph per session to
   `status/<spoke>.md`, append-only (conflict-free by construction),
   batch-merge exempt from one-topic-per-PR. Writing it is part of the
   morning-report step itself, not a separate reminder — reminders alone
   failed in the field (a spoke reached its 10th subgoal with central status
   still "No sessions yet").
2. **Inconsistency entry** — cross-repo contradictions, with the proposing
   spoke's interim resolution.
3. **ADR proposal.**
4. **Contract change.**

Each spoke's `docs/PLAN.md` remains the only tracker of its work. The hub
never mirrors spoke subgoals.

## Escalation is non-blocking

Every escalation into a human-gated channel carries an **interim decision the
spoke proceeds on** ("use the shared identity while holding to the narrower
committed policy" is the model). BRIEF re-checks pending escalations each
session; a stale escalation is re-raised in the status append, never silently
dropped and never waited on.

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
