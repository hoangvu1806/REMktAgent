---
title: "Product Brief Distillate: content_creator"
type: llm-distillate
source: "product-brief-content_creator.md"
updated: "2026-05-24"
status: current-code-aligned
---

# Product Brief Distillate

- Product: AI Real Estate Marketing Workbench.
- MVP channel: Facebook.
- Primary user: in-house real estate marketer.
- Reviewer user: marketing lead.
- Current frontend: Next.js workbench at `/` and `/projects/new`.
- Current browser API: `POST {NEXT_PUBLIC_AGENT_API_BASE_URL}/agents/chat/stream`.
- Public web: `https://mktagent.hoangvu.id.vn`.
- Public agent API: `https://apiagent.hoangvu.id.vn`.
- Product Server: FastAPI internal/local `http://127.0.0.1:8282`.
- Agent Server: FastAPI/ADK local `http://127.0.0.1:8181`.
- Rule Service: Quarkus/Kogito local `http://localhost:8080`.

Implemented:

- Project brief UI.
- Agent streaming chat.
- Product routes for projects and insights.
- Internal tools for project, insight workflow, campaign context, rule decisions, segment constraints, claim risk, and rule decision lookup.
- SQLite persistence for projects, briefs, insight snapshots, market signals, and rule decision records.
- Kogito DMN adapter with Python local-rule fallback.
- ADK hierarchy with root, intake, research, planning, generation/governance managers and specialists.

Not implemented:

- Browser Product API usage.
- Draft set persistence.
- Draft review persistence.
- Diagnostics route/view backed by persisted events.
- Missing draft review persistence and review-state transition API.
- Auth, publishing, CRM, queues, multi-user workspaces.

Core product promise:

- Convert a real estate project brief into Facebook campaign drafts with visible rationale, rule-backed planning/safety decisions, and human review control.

Next implementation priority:

1. Add draft/review persistence and routes.
2. Reintroduce a review-state transition tool only after the Product Server route exists.
3. Wire frontend to Product Server for project/insight/draft state.
4. Refresh backend tests to match current ADK/tool behavior.
