# Domain Module: Prompt / Spec / DSL Framework

Apply this module when the repository's primary content is machine-consumed definitions rather than executable code: YAML/JSON/Markdown definition trees (agent sequences, prompts, policies, templates, schemas) that dominate the file inventory, usually paired with a small compiler/validator/emitter — often an order of magnitude smaller than the definitions it processes — plus emitted or fingerprinted build outputs and closed vocabularies encoded as constants in the tool code. Boundary: if the definitions drive a staged data transformation, use `data-pipeline.md`; if the content is IaC, use `infrastructure.md`; this module is for repositories whose product is a definition language and its instances.

This module contributes topics and questions to the coverage matrix. It never names guide files — the file plan derives from the matrix.

## Required topics

Merge each topic into the coverage matrix. Any of these that is first-class in this repository is a deep-coverage candidate in the coverage matrix; the File Plan in SKILL.md decides file boundaries and counts.

- **Definition language and schema.** The DSL's node/field/step vocabulary; which vocabularies are closed sets in code versus open in prose; where the authoritative schema lives. In most of these repos the validator IS the schema's executable form — say so and cite the constants.
- **Spec-vs-implementation drift.** Fields the docs require but nothing reads, flags the emitter passes through unvalidated, prose schema claims the compiler does not check. Build an explicit contradiction ledger; this is the genre's defining failure mode and usually the guide's most valuable page.
- **Compiler / validator / emitter.** Every validation rule enumerated and mapped to code lines and covering tests; emission determinism; error behavior on invalid input.
- **Composition and inheritance.** Overlay/override/merge semantics across levels (org > domain > core, base + variant): resolution order, shadowing rules, and a WORKED example showing a child definition overriding a parent field. When composition is designed but unimplemented, label it so and sketch the intended resolution anyway — this is the topic readers of a definition framework ask about first.
- **Provenance and traceability.** Where definitions cite external sources (requirement IDs, clinical/legal references, policy documents), audit at least one citation end to end: does the definition actually implement what it cites? Recording a citation is not enforcing it; check whether any tool validates the reference.
- **Emitted substrates and consumers.** Every generated artifact, its fingerprint/versioning scheme, drift guards between definition and emission, and which downstream systems consume each substrate.
- **Vocabulary evolution.** The end-to-end playbook for extending the DSL: adding one node kind/predicate/field means touching which schema docs, which validator constants, which emitter branches, which tests, and which existing instances.
- **Governance and gating.** Review gates and phase plans, who may change definitions versus who may change the language, and the spec-versus-aspiration split: which documents describe implemented behavior today versus designed future behavior. Label every forward-looking claim.
- **Instance inventory.** The definitions themselves, one by one: purpose, provenance, size/step counts, and safety-relevant fields.
- **Testing the framework.** Tests as guarantees over the definition set — does a test cover every validation rule, and what mutation would slip through? Include the bootstrap friction for actually running them (missing requirements files are common in definition repos).

## Investigation questions

- Which fields are required by the docs but never read by the validator or emitter?
- What exactly does the compiler check, and what does it emit verbatim without checking?
- How does an instance at a lower level override a higher one, field by field — and is that implemented or designed?
- If an external citation (requirement ID, atlas step, policy clause) were wrong, what would catch it?
- What invalidates an emitted artifact, and how would a downstream consumer detect a stale substrate?
- What is the complete diff to add one new vocabulary element end to end?
- Which documents describe today's behavior and which describe a planned future — and does each say which it is?

## Traps observed in practice

- Doc-mandated fields that nothing enforces accumulate silently; inventory "required but unread" explicitly rather than assuming the validator covers the prose schema.
- A large fraction of these repos is forward-looking design prose; a guide that does not split "implemented today" from "designed" misleads every reader on every page.
- Provenance citations get repeated by docs — and by guides — without ever being audited against the cited source; demonstrate one mapping instead of restating the citation.
- The validator's closed-set constants are the real schema; prose schemas drift from them, and the drift direction tells you which one maintainers actually update.
- Placeholder apps/directories look like subsystems in a file inventory but hold only scaffolding READMEs; weigh subsystems by content, not by directory names.
