# Story 2.2: Decompose Brief Into Market Insight Questions

Status: historical-review-aligned

## Current Source-Aligned Summary

The implemented workflow decomposes a saved project brief into market research questions and a partial insight workflow bundle through:

```txt
POST /internal/tools/collect-insight-workflow
```

Specialized collection work is represented inside `AgentWorkflowService` and `InsightService` methods, not as separate FastAPI routes.

## Implemented Behavior

- `AgentWorkflowService.collect_insight_workflow()` loads the project.
- It creates market research questions from location, segment, price range, selling points, campaign objective, and buyer profile.
- It creates a persisted `MarketInsightSnapshot`.
- It returns:
  - required search agent names,
  - specialist task descriptions,
  - project facts,
  - local context placeholder signals,
  - market signal placeholder signals,
  - competitor positioning placeholder signals,
  - unavailable signal labels,
  - insight summary.

## Current Routes

Implemented:

- `POST /internal/tools/collect-insight-workflow`
- `POST /internal/tools/confirm-market-assumptions`
- `POST /projects/{project_id}/insights`
- `GET /projects/{project_id}/insights`
- `PATCH /projects/{project_id}/insights/{snapshot_id}/assumptions`

Specialized local-context, market-signal, and competitor-positioning collection currently lives inside service methods and the aggregate insight workflow response, not as separate FastAPI routes.

## Verification Target

Use current backend tests under `api/tests`, especially `test_agent_workflow_service.py`, `test_insights.py`, and `test_agent_tools.py`.
