---
workflowType: sprint-change-proposal
status: historical-aligned-summary
project_name: content_creator
user_name: Vux
date: 2026-05-24
supersedes_original_date: 2026-05-18
---

# Sprint Change Proposal: Rule-Backed Campaign Planning

This artifact records the decision to make campaign planning deterministic and rule-backed. It has been shortened to remove pre-implementation assumptions that no longer match source.

## Decision

Campaign planning outputs must come from deterministic rules through Product Server internal tools, not from freeform prompt calculation.

Implemented rule-backed tool paths:

- `POST /internal/tools/evaluate-campaign-strategy`
- `POST /internal/tools/evaluate-campaign-plan`
- `POST /internal/tools/calculate-budget-forecast`
- `POST /internal/tools/recommend-campaign-timeline`

Implemented Kogito decision-service paths:

- `POST /CampaignStrategy/EvaluateCampaignStrategy`
- `POST /CampaignPlan/EvaluateCampaignPlan`
- `POST /CampaignPlan/CalculateBudgetForecast`
- `POST /CampaignPlan/RecommendCampaignTimeline`

## Current Status

Implemented:

- DMN files for strategy and campaign planning.
- Product Server internal tool wrappers.
- Rule decision record persistence.
- Python `LocalRules` fallback.
- Planning manager and campaign planning specialist agents.

Backlog:

- Persisted campaign plan snapshots separate from rule decision records.
- Frontend Product Server integration.
- Draft set linkage to campaign plan decisions.

## Active Source Of Truth

- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
