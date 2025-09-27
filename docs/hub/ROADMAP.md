# Roadmap

## Quarterly Goals
- **Q3 2025 (ends 2025-09-30)**: Ship an integrated BA/DEV/QA MVP by completing context ingestion, automated PR review, and QA test generation flows in a single prototype build.
- **Q4 2025 (ends 2025-12-31)**: Stabilize the MVP with telemetry hooks, token-budget guardrails, and feedback capture so the hub can support iterative solo maintenance.
- **Q1 2026 (ends 2026-03-31)**: Expand observability and budgeting into dashboards, alerting, and automated throttles that span BA/DEV/QA workloads.
- **Q2 2026 (ends 2026-06-30)**: Prepare for partner onboarding by documenting runbooks, polishing deployment automation, and validating guardrails against larger sample projects.

## Upcoming Tasks
1. Finalize Firestore schemas and seed data covering briefs, backlog snapshots, and review artifacts to unblock end-to-end demos.
2. Script the context ingestion worker that listens on Pub/Sub and writes summarized briefs into Firestore.
3. Implement Vertex AI wrapper helpers for PR summarization, diff explanation, and QA test generation prompts.
4. Wire GitHub App webhooks to enqueue PR review jobs and persist automated feedback into Firestore collections.
5. Stand up minimal monitoring by tracking token spend, latency, and Pub/Sub backlog metrics within Cloud Monitoring dashboards.
6. Add scheduled cleanup tasks that trim stale context documents and enforce storage guardrails ahead of prototype handoff.
