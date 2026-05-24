---
workflowType: architecture
status: current-code-aligned
project_name: content_creator
user_name: Vux
date: 2026-05-24
source_of_truth:
  - web/src/lib/api.ts
  - api/app/main.py
  - api/app/agent_server.py
  - api/app/routes
  - api/app/services
  - api/app/agents/content_creator
  - rules-service/src/main/resources
---

# Architecture Decision Document

## Current Architecture

```text
Browser
  -> Next.js Web (mktagent.hoangvu.id.vn)
    -> FastAPI Agent Server (apiagent.hoangvu.id.vn)
      -> Google ADK Runner
        -> FastAPI Product Server internal tools
          -> SQLite
          -> Kogito Rule Service or LocalRules fallback
```

The currently implemented frontend calls the Agent Server directly. Earlier target architecture described browser-to-Product-API-only behavior; that is now a future hardening goal, not current implementation.

## Service Boundaries

### Web

- Path: `web/`
- Framework: Next.js App Router 16, React 19, TypeScript, Tailwind 4.
- Pages: `/`, `/projects/new`.
- Main component: `ProjectBriefWorkbench`.
- Runtime call: XHR streaming to `/agents/chat/stream`.
- State: mostly local React state.

### Agent Server

- Entrypoint: `api/app/agent_server.py`.
- Local URL: `http://127.0.0.1:8181`.
- Public URL: `https://apiagent.hoangvu.id.vn`.
- Route: `POST /agents/chat/stream`.
- Session store: ADK `InMemorySessionService`.
- CORS: wildcard.
- Responsibility: browser-facing streaming orchestration.

### Product Server

- Entrypoint: `api/app/main.py`.
- Local URL: `http://127.0.0.1:8282`.
- Public exposure: internal/private for current deployment.
- Routes: health, projects, insights, internal tools.
- Responsibility: product state, tool boundary, rule wrappers, persistence.

### Rule Service

- Path: `rules-service/`.
- Runtime: Quarkus/Kogito.
- Local URL: `http://localhost:8080`.
- DMN decision services:
  - `/CampaignStrategy/EvaluateCampaignStrategy`
  - `/CampaignPlan/EvaluateCampaignPlan`
  - `/CampaignPlan/CalculateBudgetForecast`
  - `/CampaignPlan/RecommendCampaignTimeline`
  - `/SegmentConstraints/CheckSegmentConstraints`
  - `/ClaimRisk/AssessClaimRisk`
- Responsibility: deterministic decision logic.

## Data Stores

SQLite file path defaults to `data/content_creator.sqlite3`.

Implemented tables:

- `projects`
- `project_briefs`
- `market_insight_snapshots`
- `market_signals`
- `rule_decision_records`

Missing tables/backlog:

- draft set records
- content draft records
- draft review decision records
- diagnostics event records
- durable chat/session tables

## API Contract Summary

### Product Routes

- `GET /health`
- `POST /projects`
- `GET /projects/{project_id}`
- `PUT /projects/{project_id}`
- `POST /projects/{project_id}/insights`
- `GET /projects/{project_id}/insights`
- `PATCH /projects/{project_id}/insights/{snapshot_id}/assumptions`

### Internal Tool Routes

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

Draft review transition is intentionally absent until draft/review persistence exists. The inactive ADK wrapper was removed so the running agent cannot call a missing Product Server route.

### Agent Route

- `POST /agents/chat/stream`

SSE chunks:

```txt
data: {"author":"...","type":"agent_event","partial":false,"text":"..."}

data: [DONE]
```

## Agent Architecture

Root agent:

- `content_creator_root_agent`: router/coordinator only.

Managers:

- `intake_manager_agent`: project creation/update/load.
- `research_manager_agent`: insight workflow and research specialist coordination.
- `planning_manager_agent`: campaign context and Kogito-backed planning.
- `generation_governance_manager_agent`: content generation and review governance.

Specialists:

- `project_fact_agent`
- `approved_source_search_agent`
- `local_context_agent`
- `market_research_agent`
- `competitor_positioning_agent`
- `persona_strategy_agent`
- `campaign_planning_agent`
- `content_generation_agent`

Important implementation detail: research specialists are currently attached through `AgentTool(...)` wrappers in `research_manager_agent.tools`; they are not active as `research_manager_agent.sub_agents`.

## Rule Architecture

FastAPI owns product-to-Kogito mapping in `KogitoRuleClient`.

If `KOGITO_RULE_SERVICE_URL` exists:

```text
Product Server -> Kogito decision-service endpoint
```

If not:

```text
Product Server -> LocalRules
```

Rule decisions are validated against Pydantic models and persisted through `RuleDecisionStore`.

## Deployment Decisions

- Publicly expose `web` and `agent_server`.
- Keep Product Server and Rule Service private/internal when possible.
- Set `NEXT_PUBLIC_AGENT_API_BASE_URL=https://apiagent.hoangvu.id.vn` before building the web app.
- Set `CONTENT_CREATOR_INTERNAL_TOOLS_BASE_URL=http://127.0.0.1:8282/internal/tools` for Agent Server.
- Ensure reverse proxy supports streaming POST/SSE and does not buffer responses.

## Architectural Gaps

1. Draft/review persistence missing.
2. Diagnostics persistence and routes missing.
3. Frontend Product API usage missing.
4. Durable session/auth/multi-user boundaries missing by design.
5. `python-dotenv` is imported by backend code but is not listed in `api/requirements.txt`; this is a dependency hygiene issue for fresh environments.
6. LocalRules and DMN parity should be reviewed where fallback logic differs.

## Future Target Architecture

The intended hardened architecture remains:

```text
Browser -> Product API facade -> Agent orchestration/internal tools -> Rules/Persistence
```

That target should be implemented only after current draft/review persistence and route gaps are closed.
