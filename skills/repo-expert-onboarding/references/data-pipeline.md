# Domain Module: Data / ETL Pipeline

Apply this module when the inventory shows staged data processing: numbered stage directories or DAG definitions, orchestrators (Airflow, Dagster, Prefect, or hand-rolled runners), source connectors/extractors, embedding or LLM-based extraction, warehouse/graph/vector stores, evaluation harnesses, or backfill/replay scripts.

This module contributes topics and questions to the coverage matrix. It never names guide files — the file plan derives from the matrix. When the pipeline is the repository's center of gravity (often the majority of the code), it dominates the coverage matrix — the classic failure is documenting the serving shell deeply while the engine gets one summarized slot.

## Required topics

Merge each topic into the coverage matrix. Any of these that is first-class in this repository is a deep-coverage candidate in the coverage matrix; the File Plan in SKILL.md decides file boundaries and counts.

- **Stage graph.** Every stage end to end: inputs, outputs, ordering, incremental versus full runs, idempotency, resume-from-failure.
- **Connectors/extractors.** A one-by-one inventory (auth, rate limits, pagination, sampling), not just the most-used connector.
- **Transformation/enrichment core.** The intellectual core of the pipeline — extraction frameworks, canonicalization, dedup. When LLM-based: model configuration, prompts, few-shot fixtures, determinism, and cost controls. If the repo exists to implement a named method or paper, that method gets deep coverage.
- **Schema handling.** Definition, canonicalization, versioning, and how schema changes propagate to already-materialized data.
- **Data products.** Naming and namespaces, versioning, which downstream consumers read each product, and what invalidates or regenerates them.
- **Storage planes.** Each store's role (relational/graph/vector/object), writers and readers, and how planes stay consistent — or observably don't.
- **Run metadata and orchestration.** Registries, run tracking, locks, concurrency limits.
- **Evaluation and quality.** Harnesses, metrics, benchmark/SOTA comparisons, gold datasets, and how a change is proven not to regress quality.
- **Backfills and lifecycle.** Replays, migrations of materialized data, retention, PII handling.
- **Cost and limits.** Paid-API spend controls, batching, caching, token/request budgets.

## Investigation questions

- What happens when a stage fails midway — what is re-run, what is duplicated, what is orphaned?
- How is a re-run made safe (idempotency keys, upserts, staging tables, namespaced products)?
- Which stages call paid APIs, and what bounds the spend of a full run?
- How do the storage planes stay consistent, and which plane is authoritative on conflict?
- Who consumes each data product, and how would a producer know it broke a consumer?
- How is extraction quality measured, and where are the fixtures and gold sets?
- Can two runs execute concurrently, and what breaks if they do?

## Traps observed in practice

- The pipeline core often dwarfs the serving apps — it can be most of the repository. Depth allocation must follow code weight, or the guide documents the shell and summarizes the engine.
- Evaluation harnesses and few-shot fixture directories are load-bearing for quality but easy to write off in one line.
- Repo docs frequently carry stale product/tool/count claims; verify counts against code and correct them explicitly.
- "The pipeline writes, the API reads" ownership claims need verification per store — maintenance scripts often write directly.
