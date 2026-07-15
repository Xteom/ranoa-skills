# Domain Module: Agent Harness

Apply this module when the inventory shows an LLM-driven agent runtime: an agent/turn loop, prompt templates, LLM SDK or gateway dependencies (`openai`, `anthropic`, `litellm`, model catalogs), tool registries, MCP/ACP/editor protocol code, conversation or session stores, or chat-platform bridges. The SDK names are examples, not an exhaustive list — a repository that runs its own tool-feeding loop through a managed runtime SDK (AWS Bedrock AgentCore, Vertex Agent Engine) in any language is the same signal. A repository that merely *calls* an LLM once is not a harness, and neither is one that only *fronts or proxies* a model runtime (an LLM gateway, a model router): an SDK dependency or a `system-prompt.md` in configs is not evidence — prove from code that a loop feeds tool results back to the model. For gateway/proxy services, use `web-app.md` and its model-gateway topics instead.

This module contributes topics and questions to the coverage matrix. It never names guide files — the file plan derives from the matrix.

## Required topics

Merge each topic into the coverage matrix. Any of these that is first-class in this repository (its own package, large module, or test domain) is a deep-coverage candidate in the coverage matrix; the File Plan in SKILL.md decides file boundaries and counts.

- **Agent loop and turn lifecycle.** Loop structure, queued input and steering, interrupts, retries, cancellation semantics, and which side effects survive a cancel. Qualify per entrypoint.
- **Message model.** How system/developer/user/tool messages are represented internally and translated per provider; where translation loses or rewrites information.
- **Prompt and context assembly.** Template system, assembly order, static-prefix/cache boundaries, progressive or conditional loading, and the exact turns and entrypoints where context is refreshed, frozen, or omitted.
- **Context management.** Token budgets, compaction/summarization triggers and algorithms, and what happens when summarization or context conversion fails mid-run.
- **Memory.** Retrieval, writes, summarization, forgetting, per-user/per-agent isolation, and exactly when memory enters or leaves the context window.
- **Tools.** How tools are exposed to the model (schemas, deferred/searchable catalogs), executed, and returned; oversized-result truncation, persistence, previewing, redaction; permissions and approval flow.
- **Model/provider adapters.** The abstraction layer, the full adapter inventory including bug-workaround or `patched_*` variants, model catalogs and their generation, provider auth/OAuth and credential storage.
- **Cost, token accounting, and rate limits.** Per-turn and per-session token/dollar accounting, budget caps and behavior at the cap, provider rate-limit handling and backoff, and per-user or per-channel quotas.
- **Middleware/interceptor chain.** If the runtime composes ordered middleware or hooks, enumerate every entry and its order. Do not compress a documented chain into a phase summary.
- **Protocol adapters and channels.** MCP, ACP, LSP, editor clients, webhooks, chat/IM platform bridges; streaming protocols, resumability, and reconnect semantics.
- **Sessions and persistence.** Session/checkpoint format, resume, replay, export, and multi-process behavior.
- **Delegation and extension.** Subagents, skills/plugins, sandboxing and execution isolation.
- **Agent testing and replay.** Fake/mock providers, recorded-transcript replay, tool mocking, deterministic fixtures and seeds, and which loop behaviors can only be tested end to end.
- **Vocabulary.** What agent, client, editor, provider, gateway, harness, and tool each mean in this repository; these words rarely mean the same thing across repos.

## Investigation questions

- What is the agent loop, file by file?
- How are system/developer/user/tool messages represented, and where are they translated per provider?
- How is prompt/context construction performed, and what invalidates any prompt cache?
- How are token budgets enforced, and what happens at the limit?
- How is memory retrieved, written, summarized, or forgotten — and at exactly which turns and entrypoints is it refreshed, frozen, or omitted?
- What happens when summarization, context conversion, or memory extraction fails?
- How are tools exposed to the model, executed, and returned? Are oversized results truncated, persisted, previewed, redacted, or retained?
- Which providers get non-standard handling (patched adapters, reasoning-field quirks, streaming differences), and why does each workaround exist?
- Which middleware/hooks run, in what order, and which mutate the model call versus merely observe it?
- What do cancellation and disconnect actually guarantee for in-flight tool calls and streamed output?
- What protocol adapters exist (ACP, MCP, LSP, chat platforms, editors), and which share the runtime versus fork their own path?
- How do sessions resume, and what state is lost on a crash between persistence points?
- How is the loop tested without live providers, and what replay/fixture infrastructure exists?

## Traps observed in practice

- The repository's own docs (`AGENTS.md`, READMEs) often enumerate middleware chains or tool counts; the guide must reproduce or explicitly correct them — stale counts are common and worth calling out.
- Prompt assembly and compaction are frequently among the largest modules by line count while looking like plumbing; check sizes before assigning depth.
- Documenting only the flagship provider adapter hides the workaround adapters where the real fragility lives.
- Chat/IM bridges look peripheral but usually carry their own auth model and streaming semantics; leaving them "summarized" routinely hides security-relevant behavior.
