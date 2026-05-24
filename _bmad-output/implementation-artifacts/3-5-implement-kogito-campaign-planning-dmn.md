# Story 3.5: Implement Kogito Campaign Planning DMN

Status: historical-review-aligned

## Current Source-Aligned Summary

Campaign planning is implemented as `CampaignPlan.dmn` plus FastAPI Product Server wrappers.

## Implemented Files

- `rules-service/src/main/resources/CampaignPlan.dmn`
- `api/app/services/kogito_rule_client.py`
- `api/app/services/local_rules.py`
- `api/app/services/rule_service.py`
- `api/app/routes/internal_tools.py`
- `api/app/models/rules.py`

## Current Endpoints

Kogito decision-service endpoints:

```txt
POST /CampaignPlan/EvaluateCampaignPlan
POST /CampaignPlan/CalculateBudgetForecast
POST /CampaignPlan/RecommendCampaignTimeline
```

FastAPI internal tool endpoints:

```txt
POST /internal/tools/evaluate-campaign-plan
POST /internal/tools/calculate-budget-forecast
POST /internal/tools/recommend-campaign-timeline
```

No separate friendly rule-service route exists for this decision; Product Server owns the friendly internal-tool paths.

## Current Output Shape

FastAPI validates and returns `CampaignPlanDecision` with budget bands, daily budget bands, KPI forecast bands, content cadence, confidence level, planning assumptions, estimate disclaimer, approval flag, rule version, formula version, and evaluated timestamp.

Rule decisions are persisted as `RuleDecisionRecord`.
