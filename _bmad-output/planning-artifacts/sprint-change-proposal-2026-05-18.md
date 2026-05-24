---
workflowType: sprint-change-proposal
status: historical-aligned-summary
project_name: content_creator
user_name: Vux
date: 2026-05-24
supersedes_original_date: 2026-05-18
---

# Sprint Change Proposal: Minimal Backend Structure

This artifact records the early decision to avoid overbuilding empty backend folders. It has been shortened to remove assumptions that no longer match the implemented source.

## Decision

Use a minimal-first backend structure and add modules only when stories need them.

Current backend source uses:

- `api/app/main.py`
- `api/app/agent_server.py`
- `api/app/routes`
- `api/app/models`
- `api/app/services`
- `api/app/storage`
- `api/app/agents`
- `api/tests`

## Current Status

Implemented:

- Product Server.
- Agent Server.
- Routes split by product/agent/internal tool concerns.
- Services for project, insight, workflow, rule, Kogito adapter, local rules.
- SQLite stores.

Backlog:

- Draft/review storage.
- Diagnostics storage.
- Durable sessions.

## Active Source Of Truth

- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
