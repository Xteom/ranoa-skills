# Domain Module: Evals / Benchmark Suite

Apply this module when the repository *is* an evaluation or benchmark suite: task/dataset definitions with gold labels, scoring or judge code, latency/throughput harnesses with results tables of percentiles or QPS, adapters for multiple systems-under-test (models, agents, vector DBs), run-matrix configs, results directories or leaderboards. A repository that merely *has* an eval harness for its own quality belongs to `data-pipeline.md`; this module is for repositories whose product is the benchmark itself. Decidable test (from the file inventory alone): classify as a benchmark suite only when the top level is dominated by system-under-test adapter directories and a results/leaderboard tree, and no deployable serving/UI/extraction app shares the workspace. If benchmark-shaped code (model zoos, comparison scripts, academic dataset schemas) sits *inside* a `stages/`, `pipeline/`, or `src/` tree alongside a deployable app or UI, it is a quality harness within that system — classify under `data-pipeline.md`.

Two genres exist and demand different rigor. **Quality benchmarks** score correctness against gold labels or judges — the gold-label, judge, contamination, and integrity topics below apply as written. **Performance benchmarks** measure latency, throughput, recall, resource use, and cost of systems-under-test — for these, the judge, contamination, and integrity topics are usually not applicable; use the two performance topics at the end of the list instead. Exception: a performance suite that reports recall or accuracy still requires the gold-label topic's ground-truth provenance and correctness — how the ground truth is generated (exact-kNN or approximate, verified or assumed) silently bounds every recall number. Many suites mix both genres; take each genre's topics for the parts that have them.

This module contributes topics and questions to the coverage matrix. It never names guide files — the file plan derives from the matrix.

## Required topics

Merge each topic into the coverage matrix. Any of these that is first-class in this repository is a deep-coverage candidate in the coverage matrix; the File Plan in SKILL.md decides file boundaries and counts.

- **Task and dataset definitions.** Task inventory, gold labels and their provenance, dataset versioning and licensing, and contamination risk — whether systems-under-test could have trained on the benchmark data.
- **System-under-test adapters.** The adapter contract: how a new model/agent/DB plugs in, what the adapter normalizes or hides (retries, prompt wrapping, temperature), and whether any adapter gives its SUT an affordance the others lack.
- **Scoring methodology.** Metrics, exact-match versus graded scoring, LLM-as-judge configuration (judge model pinning, judge prompts, judge variance), pass criteria, and aggregation into headline numbers.
- **Run orchestration.** Run matrices (SUTs × tasks × seeds), reproducibility pinning (model versions, temperature, seeds), caching of SUT responses, and resumability of interrupted sweeps.
- **Results lifecycle.** Where raw and aggregated results persist, per-run metadata, comparison across runs and benchmark versions, what invalidates old results (task edits, judge changes, harness changes), leaderboards and reports.
- **Statistical rigor.** Repeats and variance, sample sizes, confidence or significance reporting, and how noise and ties are presented.
- **Cost and limits.** Paid-API spend of a full sweep, rate limits, and the cheap smoke-run path.
- **Benchmark integrity.** Versioning of the benchmark itself, held-out sets, and defenses against overfitting to the suite.
- **Performance methodology** (performance genre). Percentile reporting (p50/p95/p99) and tail behavior, warmup and steady-state windows, concurrency and batch levels, cold-start versus warm paths, and what makes two runs comparable.
- **Measurement environment** (performance genre). Host and hardware pinning, noise isolation, resource measurement (CPU/RAM/disk), and the per-configuration sweep parameters (index and build settings) that headline numbers depend on.

## Investigation questions

- What exactly is pinned per run — model IDs, judge model, prompts, temperature, seeds — and where would an unpinned dependency hide?
- If two results tables disagree, how do you determine which harness/task/judge version produced each?
- How much does a full sweep cost, and what is the smoke-run path for validating a change cheaply?
- How is a new system-under-test added, and what must its adapter not do?
- Are judge scores stable across repeats, and where is that variance measured?
- Which stored results are stale relative to the current task and judge definitions?
- Can two sweeps run concurrently without corrupting caches or results?
- For performance suites: what pins the environment — host, warmup, dataset build — and where is run comparability enforced?

## Traps observed in practice

- Model IDs that silently resolve to updated snapshots — scores drift with no code change; check whether runs record the resolved version.
- Judge prompt edits without re-running baselines produce mixed tables that look comparable but are not.
- Adapters that quietly retry or re-prompt one SUT and not another invalidate cross-system comparisons.
- Response caches keyed too loosely serve answers from an older SUT version.
- Gold labels edited after runs leave results referencing labels that no longer exist.
