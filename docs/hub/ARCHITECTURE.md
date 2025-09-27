# Architecture Snapshot

See [detailed architecture](../architecture.md) for comprehensive diagrams and API references.

## Core Services
- **BA Agent** (FastAPI) ingests Jira issues, builds structured context packs with Vertex AI, and publishes `context.updated` events.
- **Dev Agent** (FastAPI) listens to `context.updated`/`pr.opened` topics, orchestrates pull-request automation, and updates review records.
- **QA Agent** (FastAPI) subscribes to `test.run.requested`, manages test orchestration, and records run outcomes.

## Agentspace Experience Gateway
- **Token exchange**: The gateway validates user identity, issues short-lived service tokens to the GitHub Copilot Coding Agent, and signs DEV role requests with scoped Firestore/Pub/Sub claims before dispatching work, logging each issuance for guardrail audits.
- **Job orchestration**: DEV prompts are normalized into jobs, deduplicated against active Copilot runs, and enqueued; the gateway fans each job into the Copilot Coding Agent while updating backend services (Dev Agent, Firestore) with status checkpoints that track token spend and throttle when budgets tighten.
- **Callback handling**: Streaming responses and completion callbacks from Copilot land on gateway webhooks, which reconcile job state, persist artifacts through backend APIs, and notify the UX shell via WebSocket updates, annotating which DEV-role sandbox testers initiated each run to capture context for follow-up.
- **Backend coordination**: FastAPI services remain the system-of-record for orchestration, persistence, and integrations (Firestore, Pub/Sub, Jira, GitHub, TestRail), allowing the gateway to stay stateless while reflecting Copilot progress in near real time.

## Shared Libraries
- `libs/common/google_clients.py` centralises Firestore, Pub/Sub, and Secret Manager client factories.
- `libs/common/llm.py` and `schemas.py` wrap Vertex AI Gemini responses with JSON schemas (`ContextPack`, `Review`, `TestRun`).
- `libs/common/github_client.py`, `jira_client.py`, and `testrail_client.py` provide external system connectors and shared logging.

## Google Cloud Platform Footprint
- **Pub/Sub topics**: `context.updated`, `pr.opened`, `test.run.requested` (service-to-service events).
- **Firestore collections**: `contexts/{issueKey}`, `reviews/{repo#pr}`, `tests/{repo#pr}`, `runs/{runId}` for persistent state.
- **Secret Manager**: stores API tokens and service credentials used by the agents and shared connectors.

## External Integrations
- **Vertex AI Gemini** for schema-constrained reasoning and summarisation.
- **Jira**, **GitHub**, and **TestRail** for work tracking, code review, and test management automation.

## Task Flow (BA → DEV → QA)
- **Initiate**: BA Agent retrieves Jira issue data, prompts Vertex AI with the `LLM_SCHEMA`, and saves the resulting `ContextPack` to Firestore before emitting `context.updated`.
- **Develop**: Dev Agent consumes `context.updated` to enrich pull requests, applies Vertex-backed `Review` schema outputs, and persists findings in `reviews/{repo#pr}`.
- **Validate**: QA Agent reacts to `test.run.requested`, generates `TestCase`/`TestRun` artefacts via Vertex schemas, updates Firestore `tests`/`runs`, and reports back via Pub/Sub if needed.
