# Codex Hub Overview

## Vision & Goals
- **Purpose**: Deliver a cohesive agent operations hub that aligns business analysis, development, and quality automation around a shared workflow.
- **Single front door**: Agentspace acts as the unified UX gateway where BA, DEV, and QA agents authenticate, review signals, and launch actions without tool hopping.
- **Request routing**: DEV-triggered Copilot jobs are queued in Agentspace, which stamps scoped credentials, forwards the job to the Copilot Coding Agent running in the managed services tier, and streams results back into the shared activity feed while respecting GCP free-tier throttles.
- **Roles in scope**: Business Analyst (BA) orchestrates requirement intelligence, Developer (DEV) automates code delivery by invoking the server-executed GitHub Copilot Coding Agent through DEV-role jobs, and Quality Analyst (QA) governs validation cycles with Copilot outputs folded into their reviews.
- **Infrastructure stack**: FastAPI services deployed with Gunicorn/Uvicorn, shared libraries in `libs/common`, Google Cloud Firestore for state, and Pub/Sub topics (`context.updated`, `pr.opened`, `test.run.requested`) for async coordination. See the [service architecture overview](../architecture.md#services) for details.
- **Cloud guardrails**: Prototype deployments must stay within the Google Cloud Platform free tier (Firestore, Pub/Sub, Cloud Run) until scaling thresholds are proven; Copilot job dispatch from Agentspace is throttled when free-tier limits near exhaustion, queuing non-critical runs until budgets refresh.
- **MVP outcomes**: Unified backlog triage, automated PR review prompts, and test run coordination surfaced through the hub so each role can act on current signals without switching tools.
- **Exclusions for MVP**: Marketplace integrations, adaptive prompt marketplace tooling, and automated scaling playbooks remain post-MVP roadmap items.

## Hub as the Source of Truth
- Codex Hub is the canonical repository for operational knowledge, per [ADR-0001](./DECISIONS.md#adr-0001-source-of-truth--docshub). Keeping contracts and Architectural Decision Records (ADRs) here ensures every service consumes the same definitions and message schemas.
- Shared contracts let BA, DEV, and QA agents subscribe to the same simplified event flow without drift; ADRs document why the flow exists and how future changes are governed.

## Navigate the Ecosystem
- **Role guides**: Dive into the [BA Agent](../architecture.md#services), [DEV Agent](../architecture.md#services), and [QA Agent](../architecture.md#services) service docs for runtime and integration specifics.
- **Operational checklists**: Track commitments in the [TASKS backlog](./TASKS.md) and align roadwork with the latest priorities.
- **Decisions & contracts**: Review [DECISIONS](./DECISIONS.md) for accepted ADRs and contract updates before proposing changes.
- **Prompt library**: Reference reusable conversation starters and automation triggers in [PROMPTS](./PROMPTS.md).
- **Change history**: See [CHANGELOG](./CHANGELOG.md) for release notes and iteration context.
