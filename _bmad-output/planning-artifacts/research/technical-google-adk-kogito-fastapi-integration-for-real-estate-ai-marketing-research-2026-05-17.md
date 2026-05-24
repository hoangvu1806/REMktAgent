---
workflowType: research
status: current-code-aligned-summary
research_type: technical
project_name: content_creator
user_name: Vux
date: 2026-05-24
supersedes_original_date: 2026-05-17
---

# Technical Research Summary

This file replaces the original broad technical research report with a source-aligned summary. The original report explored possible architecture patterns before implementation. The current codebase is the source of truth.

## Current Implemented Stack

- Frontend: Next.js App Router, React, TypeScript, Tailwind.
- Backend Product Server: FastAPI at `api/app/main.py`.
- Backend Agent Server: FastAPI at `api/app/agent_server.py`.
- Agent framework: Google ADK.
- Rule service: Quarkus/Kogito DMN assets.
- Persistence: SQLite through `api/app/storage`.

## Current Service Flow

```text
Browser
  -> Next.js Web
    -> FastAPI Agent Server /agents/chat/stream
      -> Google ADK agents
        -> FastAPI Product Server /internal/tools/*
          -> SQLite
          -> Kogito DMN or Python LocalRules fallback
```

## Current Ports And Public URLs

- Web local: `http://localhost:3000`
- Web public: `https://mktagent.hoangvu.id.vn`
- Agent Server local: `http://127.0.0.1:8181`
- Agent Server public: `https://apiagent.hoangvu.id.vn`
- Product Server local/internal: `http://127.0.0.1:8282`
- Rule Service local/internal: `http://localhost:8080`

## Current Rule Integration

FastAPI calls generated Kogito decision-service endpoints through `api/app/services/kogito_rule_client.py`.

Implemented decision-service paths:

- `POST /CampaignStrategy/EvaluateCampaignStrategy`
- `POST /CampaignPlan/EvaluateCampaignPlan`
- `POST /CampaignPlan/CalculateBudgetForecast`
- `POST /CampaignPlan/RecommendCampaignTimeline`
- `POST /SegmentConstraints/CheckSegmentConstraints`
- `POST /ClaimRisk/AssessClaimRisk`

When `KOGITO_RULE_SERVICE_URL` is unset, `LocalRules` provides deterministic fallback behavior.

## Current Gaps

- Frontend does not use Product Server routes yet.
- Draft sets and review decisions are not persisted.
- Diagnostics routes/events are not implemented.
- Product Server does not implement draft review state transition.
- Agent sessions are in-memory.
- Backend dependency list should include direct imports such as `python-dotenv`.

## Current Recommendations

1. Add draft/review persistence before reintroducing review-state transition tooling.
2. Add draft/review persistence before expanding product scope.
3. Wire frontend Product Server calls for saved project/insight/draft state.
4. Add diagnostics only after persisted entities exist.
5. Keep Product Server and Rule Service private behind the Agent Server for the current public deployment.
