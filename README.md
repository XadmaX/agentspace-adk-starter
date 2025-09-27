# Agentspace ADK Starter

A monorepo starter kit for building AI-assisted agents spanning business
analysis, development automation, and quality assurance workflows. Each service
is a FastAPI application with shared Google Cloud, GitHub, Jira, TestRail, and
Vertex AI integrations.

## Repository Layout

```
services/
  ba_agent/
  dev_agent/
  qa_agent/
libs/common/
infra/
.github/workflows/
.devcontainer/
.vscode/
docs/
```

## Prerequisites

- Python 3.11
- Google Cloud credentials with access to Pub/Sub, Firestore, Secret Manager
- Docker (optional for containerised development)

## Quick Start

1. **Install dependencies**

   ```bash
   make setup
   ```

2. **Run linting and tests**

   ```bash
   make lint
   make test
   ```

3. **Start a service locally**

   ```bash
   make run-local SERVICE=ba_agent
   # or SERVICE=dev_agent / qa_agent
   ```

   The FastAPI app will be available at `http://localhost:8000` with `/healthz`
   and `/readyz` endpoints.

4. **Start the Pub/Sub subscriber**

   ```bash
   python -m services.ba_agent.app.subscriber
   ```

   Replace `ba_agent` with `dev_agent` or `qa_agent` for other workers. Ensure
   the `*_PUBSUB_SUBSCRIPTION` environment variables are configured (see
   `.env.example` files).

## Config & Secrets

Shared services pull configuration from environment variables. Populate these
locally via `.env` files or a secret manager before running the agents.

### Google Cloud

- `PROJECT_ID` / `GOOGLE_CLOUD_PROJECT` – default project used for Firestore,
  Pub/Sub, Secret Manager, and Vertex AI.
- `LOCATION` – Vertex AI region (defaults to `us-central1`).
- `LOG_LEVEL` – logging verbosity for shared utilities.

### Vertex AI

- The Vertex Gemini client initialises with the Google Cloud variables above
  and uses Application Default Credentials. Ensure the runtime environment has
  access to Vertex AI Generative AI APIs.

### GitHub App

- `GITHUB_APP_ID` – numeric App identifier.
- `GITHUB_PRIVATE_KEY` – PEM encoded private key (`\n` newlines supported).
- `GITHUB_INSTALLATION_ID` – installation ID for the target organisation or
  repository.

### Jira

- `JIRA_BASE_URL` – e.g. `https://example.atlassian.net`.
- `JIRA_USER` – Jira user/email used for authentication.
- `JIRA_API_TOKEN` – API token created from Atlassian account settings.

### TestRail

- `TESTRAIL_BASE_URL` – e.g. `https://example.testrail.io`.
- `TESTRAIL_USER` – TestRail username or email.
- `TESTRAIL_API_KEY` – API key with permissions to create runs and results.

## Running with Docker

1. Build the container image:

   ```bash
   docker build -t agentspace-adk-starter .
   ```

2. Run a service:

   ```bash
   docker run --rm -it \
     -p 8000:8000 \
     --env-file services/ba_agent/.env.example \
     agentspace-adk-starter \
     gunicorn services.ba_agent.app.main:app -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
   ```

3. Run the subscriber in a separate container if required:

   ```bash
   docker run --rm -it \
     --env-file services/ba_agent/.env.example \
     agentspace-adk-starter \
     python -m services.ba_agent.app.subscriber
   ```

## Development Container

A preconfigured [Dev Container](https://containers.dev/) is available in
`.devcontainer/`. Open the repository in VS Code and choose "Reopen in Container"
for a ready-to-code environment with dependencies installed.

## Continuous Integration

GitHub Actions workflow (`.github/workflows/ci.yml`) validates formatting,
static typing, and tests on pushes and pull requests targeting `main`.

## License

[MIT License](LICENSE)

