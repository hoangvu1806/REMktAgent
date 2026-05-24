---
workflowType: prd
workflow: edit
status: current-code-aligned
project_name: content_creator
product_name: AI Real Estate Marketing Workbench
user_name: Vux
date: 2026-05-24
lastEdited: 2026-05-24
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
supersedes:
  - _bmad-output/planning-artifacts/prd-validation-report.md
  - _bmad-output/planning-artifacts/implementation-readiness-report-2026-05-18.md
---

# Product Requirements Document - content_creator

## Executive Summary

`content_creator` is an AI Real Estate Marketing Workbench for generating Facebook campaign content from structured real estate project briefs. The product combines a Next.js workbench, FastAPI Product Server, FastAPI Agent Server, Google ADK agents, SQLite MVP persistence, and Kogito/local deterministic rules.

The current implementation is a working agent-stream prototype, not a fully persisted campaign management system. The browser calls the Agent Server directly through `POST /agents/chat/stream`; Product Server routes exist for projects, insights, internal agent tools, and rule decisions; draft/review/diagnostics persistence is still backlog.

## Product Positioning

The product is not a generic caption generator. It is a governed AI campaign workbench for real estate Facebook content, where agent reasoning and deterministic rules help marketers understand why draft options were produced and what needs human review.

## Users

- **Primary user:** In-house real estate marketer preparing Facebook campaign posts.
- **Reviewer:** Marketing lead reviewing draft quality and claim risk.
- **Internal operator/developer:** Person validating agent routing, rule decisions, persistence, and deployment health.
- **Future user:** Agency team managing multiple real estate client campaigns.

## Current Runtime

| Service | Local URL | Public URL | Status |
|---|---:|---:|---|
| Web | `http://localhost:3000` | `https://mktagent.hoangvu.id.vn` | implemented |
| Agent Server | `http://127.0.0.1:8181` | `https://apiagent.hoangvu.id.vn` | implemented |
| Product Server | `http://127.0.0.1:8282` | internal only | implemented |
| Rule Service | `http://localhost:8080` | internal only | optional; local fallback exists |

## Implemented Capabilities

### FE-1 Workbench UI

The web app renders `ProjectBriefWorkbench` at `/` and `/projects/new`.

The workbench supports:

- project brief form fields,
- chat stream panel,
- workflow views for `Brief`, `Insights`, `Drafts`, and `Review`,
- local draft cards,
- local draft status changes,
- local campaign plan display parsed from streamed text,
- mock/static insight examples and heuristic text parsing.

### FE-2 Agent Streaming

The frontend calls:

```txt
POST {NEXT_PUBLIC_AGENT_API_BASE_URL}/agents/chat/stream
```

The current public value is:

```txt
https://apiagent.hoangvu.id.vn/agents/chat/stream
```

The frontend does not currently use `NEXT_PUBLIC_API_BASE_URL`.

### BE-1 Product Routes

Product Server implements:

- `GET /health`
- `POST /projects`
- `GET /projects/{project_id}`
- `PUT /projects/{project_id}`
- `POST /projects/{project_id}/insights`
- `GET /projects/{project_id}/insights`
- `PATCH /projects/{project_id}/insights/{snapshot_id}/assumptions`

### BE-2 Agent Route

Agent Server implements:

- `POST /agents/chat/stream`

The route uses Google ADK `Runner`, `InMemorySessionService`, and SSE-style `text/event-stream` chunks.

### BE-3 Internal Tool Routes

Product Server implements these ADK-callable internal tools:

- `POST /internal/tools/collect-project-facts`
- `POST /internal/tools/create-project`
- `POST /internal/tools/update-project`
- `GET /internal/tools/get-project/{project_id}`
- `POST /internal/tools/collect-insight-workflow`
- `POST /internal/tools/confirm-market-assumptions`
- `POST /internal/tools/prepare-campaign-context`
- `POST /internal/tools/evaluate-campaign-strategy`
- `POST /internal/tools/evaluate-campaign-plan`
- `POST /internal/tools/calculate-budget-forecast`
- `POST /internal/tools/recommend-campaign-timeline`
- `POST /internal/tools/check-segment-constraints`
- `POST /internal/tools/assess-claim-risk`
- `GET /internal/tools/rule-decisions/{project_id}`

Known gap: draft review persistence and review-state transition APIs are not implemented. The inactive ADK review-state wrapper has been removed until that backend surface exists.

### BE-4 Persistence

SQLite persists:

- projects,
- project briefs,
- market insight snapshots,
- market signals,
- rule decision records.

Not persisted yet:

- chat sessions,
- draft sets,
- content drafts,
- draft review decisions,
- diagnostics events.

### BE-5 Agent Topology

The ADK hierarchy is:

- `content_creator_root_agent`
- `intake_manager_agent`
  - `project_fact_agent`
- `research_manager_agent`
  - uses internal workflow tools and `AgentTool` wrappers for research specialists
  - research specialists use ADK `google_search`
- `planning_manager_agent`
  - `persona_strategy_agent`
  - `campaign_planning_agent`
- `generation_governance_manager_agent`
  - `content_generation_agent`

### RULE-1 Rules

Rule assets:

- `CampaignStrategy.dmn`
- `CampaignPlan.dmn`
- `SegmentConstraints.dmn`
- `ClaimRisk.dmn`

FastAPI maps product-oriented rule calls to Kogito decision-service paths. If Kogito is not configured, Python `LocalRules` is used.

## Functional Requirements

### Implemented

- FR1: User can open the workbench without login.
- FR2: User can enter project brief fields: project name, segment, location, price range, key selling points, campaign objective, buyer profile, tone, and promotion details.
- FR3: Browser can stream agent responses from the Agent Server.
- FR4: Agent workflow can create, load, and update projects through Product Server internal tools.
- FR5: Product Server can persist and retrieve project briefs.
- FR6: Product Server can create/list insight snapshots and update assumptions.
- FR7: Agent workflow can create a partial insight workflow bundle with questions, summary sections, unavailable signals, and specialist tasks.
- FR8: Agent workflow can evaluate campaign strategy, campaign plan, budget forecast, timeline, segment constraints, and claim risk through internal tools.
- FR9: Product Server can persist rule decision records.
- FR10: UI can display streamed draft-like content and local review state.

### Backlog

- FR11: Browser can save/read project and insight state through Product Server.
- FR12: Product Server can persist draft sets and generated draft candidates.
- FR13: Product Server can persist draft review status and review notes.
- FR14: Product Server can add draft review persistence and then reintroduce a review-state transition tool.
- FR15: UI can load persisted drafts/reviews instead of relying on local React state.
- FR16: Diagnostics API can expose health, rule decisions, insight state, draft count, generation status, and error categories.
- FR17: Tests are refreshed so they assert current ADK `AgentTool` topology and timeout defaults.
- FR18: Public deployment config prevents `127.0.0.1` frontend fallbacks from leaking into production builds.

## Non-Functional Requirements

- NFR1: Frontend production builds must set `NEXT_PUBLIC_AGENT_API_BASE_URL=https://apiagent.hoangvu.id.vn`.
- NFR2: Agent Server must support long-lived streaming POST responses and disable proxy buffering where applicable.
- NFR3: Product Server and Rule Service may remain internal if Agent Server can reach them.
- NFR4: Both FastAPI apps currently allow all CORS origins; this is acceptable for the current public prototype and should be tightened before handling sensitive/multi-user data.
- NFR5: No generated content is considered approved unless explicit human review state exists.
- NFR6: Rule outputs are estimates/guardrails, not legal, financial, investment, or performance guarantees.
- NFR7: SQLite is acceptable for MVP state.
- NFR8: Agent sessions are volatile until durable session persistence is implemented.
- NFR9: Internal tools must use the Product Server boundary, not raw Kogito endpoints.
- NFR10: The browser must not call Kogito directly.

## Explicit Exclusions

- Authentication and RBAC.
- Organization workspaces.
- Auto-publishing or scheduling.
- CRM or lead nurturing automation.
- Paid media bidding automation.
- Multi-channel generation beyond Facebook.
- PostgreSQL or queue workers unless later justified.

## Acceptance Criteria For Current Release

- Web loads at `https://mktagent.hoangvu.id.vn`.
- Web calls `https://apiagent.hoangvu.id.vn/agents/chat/stream`.
- Agent Server can reach Product Server at `CONTENT_CREATOR_INTERNAL_TOOLS_BASE_URL`.
- Product Server can create project, insight, and rule decision records.
- Kogito calls work when `KOGITO_RULE_SERVICE_URL` is configured; otherwise local rules produce deterministic fallback outputs.
- Documentation distinguishes implemented behavior from backlog.

## Next BMAD Implementation Priority

1. Add draft set and review persistence.
2. Reintroduce a review-state transition tool only after the Product Server route exists.
3. Wire frontend to Product Server for saved project/insight/draft state.
4. Add diagnostics route/view.
5. Reconcile tests with current code behavior.
