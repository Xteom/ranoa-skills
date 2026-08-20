# Domain Module: Memory / Retrieval Engine

Apply this module when the repository's product is a queryable memory or retrieval store: a memory/fact schema (entries with versioning, supersession, or forgetting fields), embedding generation (local models or API calls), chunking code, vector/graph indexes, and search endpoints with quality knobs (modes, thresholds, reranking, query rewriting). Boundary: `agent-harness.md` owns memory as a subsystem feeding one agent's context window; this module owns repositories where the memory/retrieval store IS the product, serving external clients. A repo whose staged pipeline materializes versioned data products for downstream batch consumers is `data-pipeline.md`; many knowledge-graph platforms legitimately match both — take both topic sets.

This module contributes topics and questions to the coverage matrix. It never names guide files — the file plan derives from the matrix.

## Required topics

Merge each topic into the coverage matrix. Any of these that is first-class in this repository is a deep-coverage candidate in the coverage matrix; the File Plan in SKILL.md decides file boundaries and counts.

- **Fact/memory lifecycle.** Creation, versioning and supersession chains (parent/root/is-latest invariants), conflict handling when a new fact contradicts a stored one, forgetting and expiry semantics, and static-versus-inferred provenance. State precisely what "forget" and "delete" each guarantee, per storage plane.
- **Ingestion path.** Document → chunk → extraction → memory writes, end to end. If extraction is LLM-agentic, treat it as a real agent loop (tools, step/token caps, retries — the `agent-harness.md` loop topics apply to it) and document what happens to content past the caps. Idempotency, dedup, and safe re-ingestion.
- **Chunking and provenance.** Chunking strategies, chunk→memory traceability keys, and what survives re-chunking or document updates.
- **Embedding lifecycle.** Which models (local/bundled versus API), dimensions and pinning, what happens to existing vectors when the embedding model changes, and index build/maintenance/migration.
- **Retrieval pipeline.** Every search mode and its dispatch path; defaults for thresholds, container/scope tags, and limits; reranking, query rewriting, hybrid fusion, temporal filters. Enumerate the knobs exposed to callers versus hardcoded.
- **Relation/knowledge graph.** Relation types and scores, and — verified, not assumed — whether the graph actually participates in retrieval/ranking or is write-only decoration.
- **Tenancy and scoping.** The org/container/user keys on every plane (rows, embeddings, indexes, caches), and which plane could leak across scopes.
- **Retrieval quality evaluation.** Benchmarks, gold sets, recall/precision measurement, and whether a quality regression would be caught before shipping. If a sibling benchmark repo exists, name it and the linkage.
- **Cost and capacity.** Embedding plus extraction-LLM spend per document, storage growth per memory, index size, and any batching/caching that bounds them.

## Investigation questions

- When a new fact contradicts a stored one, what exactly happens — supersede, duplicate, merge, or nothing? Which code decides?
- What does "forget" guarantee: row deletion, tombstone, retrieval exclusion, embedding removal — and on which planes is the memory still physically present?
- What happens to stored vectors and indexes when the embedding model or dimension changes?
- Which retrieval defaults (threshold, scope tag, limit, mode) silently shape recall, and where are they set?
- Does the relation graph affect ranking, or is it never read on the query path?
- How is retrieval quality measured, and what would catch a regression?
- Can two ingestions of the same document run concurrently, and what dedupes the resulting memories?
- Which supersession/is-latest invariant does every query respect — and is there one query that forgets to?

## Traps observed in practice

- Docs claim retrieval capabilities (FTS, graph search, hybrid) that the shipped query path does not implement; trace the actual search dispatch before repeating any capability claim.
- "Forgotten" or "deleted" memories routinely survive in embeddings, indexes, or caches; verify deletion on every plane, not just the primary table.
- Supersession chains impose is-latest invariants across all reads; the interesting bug is the one query path that skips the filter.
- Default thresholds and default scope tags are load-bearing for recall and rarely documented; enumerate them with their exact values.
- LLM extraction agents carry step and output-token caps that silently truncate large documents — find the caps and state what is lost past them.
- Bundled local embedding models are effectively unversioned unless something fingerprints them; re-embedding drift is invisible without it.
