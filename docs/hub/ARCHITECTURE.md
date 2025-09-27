# Architecture Snapshot

See [detailed architecture](../architecture.md) for comprehensive diagrams and API references.

## Core Services
- **BA Agent** (FastAPI) ingests Jira issues, builds structured context packs with Vertex AI, and publishes `context.updated` events.
- **Dev Agent** (FastAPI) listens to `context.updated`/`pr.opened` topics, orchestrates pull-request automation, and updates review records.
- **QA Agent** (FastAPI) subscribes to `test.run.requested`, manages test orchestration, and records run outcomes.

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
