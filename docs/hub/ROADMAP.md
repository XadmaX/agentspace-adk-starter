# Roadmap

## Quarterly Goals
- **Q3 2025 (ends 2025-09-30)**: Ship an integrated BA/DEV/QA MVP and deliver Agentspace onboarding flows that guide each role from login through first-task completion.
- **Q4 2025 (ends 2025-12-31)**: Stabilize the MVP with telemetry hooks, token-budget guardrails, and Copilot-assisted DEV workflows wired through Agentspace widgets.
- **Q1 2026 (ends 2026-03-31)**: Expand observability and budgeting into dashboards, alerting, and automated throttles that span BA/DEV/QA workloads while monitoring Copilot usage and spend.
- **Q2 2026 (ends 2026-06-30)**: Prepare for partner onboarding by documenting runbooks, polishing deployment automation, and validating guardrails (including GCP free-tier budgets) against larger sample projects.

## Upcoming Tasks
1. Finalize Firestore schemas and seed data covering briefs, backlog snapshots, and review artifacts to unblock end-to-end demos.
2. Script the context ingestion worker that listens on Pub/Sub and writes summarized briefs into Firestore.
3. Implement Agentspace onboarding journeys (role-specific checklists, guardrail prompts, and access verification) surfaced in the UX gateway.
4. Wire GitHub Copilot context sharing to the Dev Agent so inline suggestions reflect the latest backlog and review signals.
5. Stand up minimal monitoring by tracking token spend, Copilot usage, latency, and Pub/Sub backlog metrics within Cloud Monitoring dashboards.
6. Add scheduled cleanup tasks that trim stale context documents and enforce storage guardrails (Firestore, Pub/Sub quotas, Copilot token budgets) ahead of prototype handoff.
