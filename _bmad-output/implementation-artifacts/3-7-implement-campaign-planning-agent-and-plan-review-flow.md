# Story 3.7: Implement Campaign Planning Agent And Plan Review Flow

Status: historical-aligned-summary

## Current Source-Aligned Summary

Planning agent wiring exists. Product UI plan review remains local/heuristic and is not persisted as a separate campaign plan entity.

Implemented files:

- `api/app/agents/content_creator/planning_manager_agent.py`
- `api/app/agents/content_creator/tools.py`
- `api/app/services/agent_workflow_service.py`
- `api/app/routes/internal_tools.py`

Implemented behavior:

- `planning_manager_agent` can call `prepare_campaign_context`.
- `campaign_planning_agent` can call campaign plan, budget forecast, and timeline tools.
- Rule-backed planning outputs are persisted as rule decision records.

Current gaps:

- No separate campaign plan snapshot table.
- Frontend plan panel is parsed from streamed text and local state.
- Draft generation persistence does not yet link to a campaign plan snapshot.
