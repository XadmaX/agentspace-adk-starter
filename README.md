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

