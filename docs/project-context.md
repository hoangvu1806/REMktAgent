# Project Context: content_creator

Status: current-code-aligned as of 2026-05-24.

## Product

AI Real Estate Marketing Workbench for Facebook campaign content generation. The product combines agent-assisted reasoning, deterministic rule checks, and human review control for real estate marketing teams.

## Current Runtime

| Boundary | Local | Public | Notes |
|---|---:|---:|---|
| Web | `http://localhost:3000` | `https://mktagent.hoangvu.id.vn` | Next.js workbench |
| Agent Server | `http://127.0.0.1:8181` | `https://apiagent.hoangvu.id.vn` | Browser-facing ADK SSE stream |
| Product Server | `http://127.0.0.1:8282` | internal | Product APIs and internal tools |
| Rule Service | `http://localhost:8080` | internal | Optional Kogito DMN runtime |

## Current Browser Call

The frontend currently calls only:

```txt
POST {NEXT_PUBLIC_AGENT_API_BASE_URL}/agents/chat/stream
```

`NEXT_PUBLIC_API_BASE_URL` exists but is not currently used by `web/src`.

## Implemented

- Next.js workbench at `/` and `/projects/new`.
- FastAPI Agent Server streaming endpoint.
- FastAPI Product Server project and insight routes.
- FastAPI internal tool routes for project, insight workflow, campaign context, rule decisions, segment constraints, claim risk, and rule decision lookup.
- SQLite persistence for projects, briefs, insight snapshots, market signals, and rule decision records.
- Google ADK agent hierarchy for intake, research, planning, generation/governance.
- Kogito DMN integration with Python `LocalRules` fallback.

## Not Implemented Yet

- Frontend Product Server integration.
- Draft set persistence.
- Draft review persistence.
- Diagnostics API/events.
- Draft review transition route/tool is not implemented; the inactive ADK wrapper was removed until draft/review persistence exists.
- Durable chat/session persistence.
- Auth, RBAC, multi-user workspaces, queues, publishing, CRM, analytics.

## Active BMAD Documents

- `_bmad-output/planning-artifacts/prd.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `README.md`
- `docs/dmn-rule-specification.md`

Older planning/research/story files are retained as history unless explicitly referenced by the active files above.
