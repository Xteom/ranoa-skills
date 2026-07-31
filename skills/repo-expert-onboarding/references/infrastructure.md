# Domain Module: Infrastructure / GitOps Platform

Apply this module when the repository's primary content is infrastructure: Terraform/Pulumi/CDK/CloudFormation stacks, Kubernetes manifests, Helm charts or Kustomize overlays, Argo/Flux GitOps configs, or Ansible playbooks — with little or no application source. An application repo that merely *contains* an `infra/` directory belongs to `web-app.md`'s deployment topics; this module is for repositories whose product is the infrastructure itself.

This module contributes topics and questions to the coverage matrix. It never names guide files — the file plan derives from the matrix.

## Required topics

Merge each topic into the coverage matrix. Any of these that is first-class in this repository is a deep-coverage candidate in the coverage matrix; the File Plan in SKILL.md decides file boundaries and counts.

- **Stack and module inventory.** Every stack/root module, the real-world resources each owns, and the dependency graph between stacks (remote state references, stack outputs, cross-stack imports).
- **State management.** Where state lives, locking, who can access it raw, drift and import procedures, and any history of state surgery.
- **Environments and promotion.** How dev/staging/prod actually differ (workspaces, directories, branches, overlays), what promotes a change between them, and which differences are intentional versus drift. Enumerate the deltas; do not trust the naming.
- **Change lifecycle.** The plan/apply flow: who runs it (CI, humans, a GitOps controller), approval gates, what a merge to the default branch actually triggers, and the rollback story.
- **GitOps reconciliation** (when present). Controllers, sync policies, prune behavior, and what happens to manual cluster edits.
- **Secrets and identity.** How secrets enter infrastructure (SOPS, Vault, cloud secret managers), the credentials CI holds, OIDC/workload identity, and the blast radius of the pipeline's role.
- **Blast radius and safety.** Which changes force resource replacement, deletion-protection and lifecycle rules, what a bad apply can take down, and the disaster-recovery path.
- **Module/chart authoring.** Internal modules and charts: versioning, the consumption contract, and how upgrades roll out across consumers.
- **Ownership boundaries.** Which teams or repos consume which stack outputs, and what is managed here versus by application repos versus by hand.
- **Cost and quotas.** Cost-relevant knobs, budget guardrails, and quota constraints that shape the design.

## Investigation questions

- What does a merge to the default branch actually do, and is anything ever applied outside CI?
- Where is state stored and locked, and who can read or edit it directly?
- How would drift between cloud and code be detected — is anything scheduled, or only discovered at the next plan?
- Which resources would a naive re-apply destroy or replace, and which carry deletion protection?
- How is a new stack, environment, or service bootstrapped end to end — including the chicken-and-egg steps?
- What secrets does the pipeline hold, and what could a compromised pipeline reach?
- What is the rollback procedure, and is there evidence it has ever been exercised?

## Traps observed in practice

- Live versus fossil stacks: repositories accumulate a second IaC stack during migrations; the guide must say which one deploys today, or operators will apply the dead one.
- "Everything is in Terraform" is usually false — inventory the click-ops resources and anything imported but never reconciled.
- Environment parity claims hide hand-applied production hotfixes that never landed in code.
- State files hold secrets in plaintext more often than teams assume; check what the backend stores and who can read it.
- GitOps with pruning disabled means resources deleted in git live on in the cluster indefinitely.
