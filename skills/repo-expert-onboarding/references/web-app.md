# Domain Module: Web App / Service Monorepo

Apply this module when the inventory shows HTTP services or web frontends: frontend frameworks (Next.js, React, Vue, Svelte), server frameworks (FastAPI, Express, Hono, Rails, Spring), an HTTP listener in any language (Go `net/http`/gin/echo/chi, Rust axum/actix, a `cmd/*/main` that binds a port), ORMs and migrations, reverse-proxy configs (nginx, Caddy), docker-compose/Kubernetes/IaC directories, or multiple deployable apps in a workspace. If the repository's primary content is IaC with little application source, use `infrastructure.md` instead.

This module contributes topics and questions to the coverage matrix. It never names guide files — the file plan derives from the matrix.

## Required topics

Merge each topic into the coverage matrix. Any of these that is first-class in this repository (its own app, service, or infra stack) is a deep-coverage candidate in the coverage matrix; the File Plan in SKILL.md decides file boundaries and counts.

- **Service topology and ownership.** Every deployable app/service, what it owns, which service owns each datastore, workspace/build orchestration (pnpm/turbo/nx), and inter-service contracts. Verify ownership claims against every service, not against the repo's own docs.
- **Frontend.** Routing, SSR/CSR/hydration boundaries, state management, the API client layer, and the build/runtime env split — including which env vars are compiled into the client bundle.
- **Backend APIs.** Route inventory per service, transport formats, streaming (SSE/WebSocket), versioning, error contracts.
- **Ingress and proxy.** Enumerate public routes from the proxy/deployment config, not from application routers; identify direct-service bypasses, auth-exempt routes, and TLS assumptions.
- **Model gateway / LLM proxy** (when the service's primary job is routing or proxying LLM/model-runtime calls). Provider adapter inventory and routing/fallback policy, the model catalog, token/cost accounting and per-tenant quotas, streaming passthrough and backpressure, provider rate-limit handling and backoff, and request/response transformation. This is the owning topic set for gateway repos that `agent-harness.md` excludes for lack of a tool-feeding loop.
- **Data model.** Schemas, migrations and their bootstrap story, tenancy/ownership keys, indexes that encode invariants.
- **AuthN/AuthZ.** Sessions/JWT/OIDC flows, CSRF strategy, service-to-service auth, internal tokens.
- **Background work.** Jobs, queues, schedulers, retries, and what happens to in-flight work on deploy.
- **Deployment and infrastructure.** Every IaC stack — state explicitly which is live and which is frozen or legacy — container builds, environment matrix, runbooks, backup/restore. When more than one stack or environment exists, deployment is a first-class deep-coverage candidate in the matrix; the File Plan decides whether it stands alone.
- **Client-side persistence.** localStorage/IndexedDB/cookies as real persistence planes with their own lifecycle.
- **Observability.** Logs, metrics, tracing, health checks — per service, not globally.

## Investigation questions

- Which public routes bypass the primary application or its authentication layer?
- How do frontend and backend share types/contracts, and what breaks silently when they drift?
- What is the minimal local run path, and which services fail without Docker or external credentials?
- Which env vars reach the browser bundle, and do any carry secrets?
- Which migrations run automatically versus manually, and in what order at first boot?
- What exactly happens on deploy: draining, in-flight jobs, cache invalidation, session survival?
- For each datastore: who writes, who reads, and does any service bypass the owning API?

## Traps observed in practice

- Two IaC stacks where only one is live: the guide must say which, or operators will deploy the fossil.
- `NEXT_PUBLIC_*`-style variables holding API keys — check for secrets leaking into client bundles.
- The proxy config is the real trust boundary; application-level route lists routinely miss direct-service routes.
- "Only service X touches the database" is usually aspirational; grep every service for connection strings before repeating it.
