# Roadmap

## Quarterly Goals
- **Q3 2025 (ends 2025-09-30)**: Ship an integrated BA/DEV/QA MVP, deliver Agentspace onboarding flows, and pilot a Copilot Coding Agent sandbox with DEV role testers.
- **Q4 2025 (ends 2025-12-31)**: Stabilize the MVP with telemetry hooks, codify Copilot guardrails (token budgets, repository scopes), and graduate the sandbox to limited production via Agentspace widgets.
- **Q1 2026 (ends 2026-03-31)**: Expand observability and budgeting into dashboards, alerting, and automated throttles while layering Copilot usage telemetry into capacity planning.
- **Q2 2026 (ends 2026-06-30)**: Prepare for partner onboarding by documenting runbooks, polishing deployment automation, and validating Copilot guardrails (including GCP free-tier budgets) against larger sample projects.

## Upcoming Tasks
1. Finalize Firestore schemas and seed data covering briefs, backlog snapshots, and review artifacts to unblock end-to-end demos.
2. Script the context ingestion worker that listens on Pub/Sub and writes summarized briefs into Firestore.
3. Implement Agentspace onboarding journeys (role-specific checklists, guardrail prompts, and access verification) surfaced in the UX gateway.
4. Wire GitHub Copilot context sharing to the Dev Agent so inline suggestions reflect the latest backlog and review signals.
5. Launch a Copilot Coding Agent sandbox environment, capture qualitative feedback from DEV-role sandbox participants exercising the agent end to end, and iterate on prompt/guardrail tuning before broad release.
6. Stand up minimal monitoring by tracking token spend, Copilot usage, latency, and Pub/Sub backlog metrics within Cloud Monitoring dashboards.
7. Add scheduled cleanup tasks that trim stale context documents and enforce storage guardrails (Firestore, Pub/Sub quotas, Copilot token budgets) ahead of prototype handoff.
