# Agentspace ADK Starter Architecture

This monorepo hosts three FastAPI-based services that interact with shared
libraries for Google Cloud integrations, test management systems, and GitHub.

## Services

- **BA Agent** — manages business analysis contexts and listens to
  `context.updated` events.
- **Dev Agent** — performs development-oriented automation when pull requests
  are opened and listens to `pr.opened` messages.
- **QA Agent** — coordinates testing workflows, reacting to
  `test.run.requested` events.

Each service exposes `GET /healthz` and `GET /readyz` endpoints and can be run
with Gunicorn using the Uvicorn worker for production deployments.

## Shared Libraries

Common functionality such as Google Cloud clients, GitHub integrations, Jira
and TestRail connectors, Vertex AI wrappers, and shared Pydantic schemas live in
`libs/common`. These modules are intended to be reused across services and keep
business logic lean within the individual agents.

## Data Stores

Firestore collections are structured as follows:

- `contexts/{issueKey}`: `summary`, `risks[]`, `acceptance[]`, `links[]`, `embeddings[]`
- `reviews/{repo#pr}`: `findings[]`, `suggested_changes[]`, `status`, `author`
- `tests/{repo#pr}`: `cases[]`, `traceability` (AC→case), `status`
- `runs/{runId}`: `startedAt`, `finishedAt`, `tool`, `artifacts[]`, `status`, `links[]`

## Messaging

Google Cloud Pub/Sub topics are defined for cross-service communication:

- `context.updated`
- `pr.opened`
- `test.run.requested`

Subscribers for each service are implemented in dedicated entrypoints that can
be run as background workers alongside the web servers.

