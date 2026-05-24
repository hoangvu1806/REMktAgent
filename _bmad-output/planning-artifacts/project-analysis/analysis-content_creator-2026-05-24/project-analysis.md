---
stepsCompleted:
  - step-01-intake
  - step-02-source-review
  - step-03-current-state-analysis
  - step-04-route-recommendation
workflowType: project-analysis
lastStep: 4
project_slug: content_creator
project_name: content_creator
user_name: Vux
date: 2026-05-24
status: current-code-aligned
confidence: high
source_of_truth:
  - README.md
  - web/src/lib/api.ts
  - web/src/components/features/project-brief/project-brief-workbench.tsx
  - api/app/main.py
  - api/app/agent_server.py
  - api/app/routes
  - api/app/services
  - api/app/agents/content_creator
  - rules-service/src/main/resources
recommended_next_workflow: bmad-quick-dev
---

# Project Analysis: content_creator

## Intake Snapshot

`content_creator` is an AI Real Estate Marketing Workbench. The implemented code is an MVP prototype with three runtime services:

- Next.js web app at `web/`.
- FastAPI Product Server at `api/app/main.py`.
- FastAPI Agent Server at `api/app/agent_server.py`.
- Quarkus/Kogito rule service at `rules-service/`.

Current public mapping:

- Web: `https://mktagent.hoangvu.id.vn`.
- Agent API: `https://apiagent.hoangvu.id.vn`.
- Product API: internal/local `http://127.0.0.1:8282`.
- Rule service: internal/local `http://localhost:8080`.

## Current Evidence From Source

Frontend:

- `/` and `/projects/new` both render `ProjectBriefWorkbench`.
- Browser currently calls only `NEXT_PUBLIC_AGENT_API_BASE_URL + /agents/chat/stream`.
- `NEXT_PUBLIC_API_BASE_URL` exists but is not used by `web/src`.
- Workbench state for drafts, review status, parsed campaign plan, and insight display is client-side only.

Backend:

- Product Server exposes `/health`, `/projects`, `/projects/{project_id}`, project insight routes, and `/internal/tools/*`.
- Agent Server exposes `POST /agents/chat/stream` with ADK `Runner` and in-memory sessions.
- CORS is open to all origins on both FastAPI apps.
- SQLite persists projects, briefs, insight snapshots, market signals, and rule decision records.
- Draft sets, draft review decisions, review notes, diagnostics events, and review-state transition APIs are not implemented.

Agent layer:

- Root: `content_creator_root_agent`.
- Managers: `intake_manager_agent`, `research_manager_agent`, `planning_manager_agent`, `generation_governance_manager_agent`.
- Specialists include project fact, approved source search, local context, market research, competitor positioning, persona strategy, campaign planning, and content generation agents.
- Google Search is used only by research specialists in `research_manager_agent.py`.
- Internal tool wrappers call Product Server through `CONTENT_CREATOR_INTERNAL_TOOLS_BASE_URL`.

Rules:

- DMN assets: `CampaignStrategy.dmn`, `CampaignPlan.dmn`, `SegmentConstraints.dmn`, `ClaimRisk.dmn`.
- FastAPI maps Product-level rule requests to generated Kogito endpoints.
- If `KOGITO_RULE_SERVICE_URL` is unset, Python `LocalRules` provides deterministic fallback.

## Problem And User

Real estate marketers need faster Facebook campaign draft preparation without losing campaign logic, market assumptions, review discipline, or safety checks around sensitive claims.

Primary user: in-house real estate marketer.

Secondary user: marketing lead/reviewer.

Internal user: operator/developer validating agent, rule, and persistence behavior.

## Current Product State

Implemented vertical slice:

- Workbench UI can collect a brief and stream a multi-agent response.
- Agent workflow can create/update/load projects through internal tools.
- Research workflow can create partial insight snapshots and expose follow-up questions/gaps.
- Planning workflow can call Kogito/local rule-backed decisions.
- Content generation agents exist and can stream text through chat.
- UI can parse streamed text into draft-like cards, but those cards are not schema-persisted.

Main gaps:

- No browser Product API integration.
- No persisted draft/review API.
- No diagnostics API/view backed by persisted diagnostics records.
- Review-state transition tooling is absent until Product Server draft/review persistence exists.
- Backend tests have known drift from current code behavior.

## Risks

- Documentation drift if planned routes are described as implemented.
- Deployment confusion if frontend is built with `127.0.0.1:8181` instead of `https://apiagent.hoangvu.id.vn`.
- Runtime review-state transition is unavailable by design until the backend route exists.
- Loss of draft/review traceability because current UI status updates are client-side only.
- Public Agent Server can reach Product Server only if `CONTENT_CREATOR_INTERNAL_TOOLS_BASE_URL` points to the internal Product Server.

## Route Recommendation

Recommended next workflow: `bmad-quick-dev`.

Reason: planning is now sufficiently clear; the next valuable work is implementation hardening:

1. Add Product Server draft/review persistence and reintroduce review-state transition tooling only after the route exists.
2. Add persisted draft set and draft review APIs.
3. Wire frontend Product API calls for project/insight/draft persistence.
4. Refresh backend tests to match current ADK/tool behavior.

## Decision Log

- 2026-05-24: Treat `README.md`, service README files, PRD, architecture, epics, UX, and sprint status as current planning source of truth.
- 2026-05-24: Mark old implementation story files as historical unless referenced by current `sprint-status.yaml`.
- 2026-05-24: Keep code unchanged; documentation is aligned to current implementation and public deployment config.
