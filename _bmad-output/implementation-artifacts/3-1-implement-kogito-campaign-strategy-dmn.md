# Story 3.1: Implement Kogito Campaign Strategy DMN

Status: historical-review-aligned

## Current Source-Aligned Summary

Campaign strategy is implemented as a Kogito DMN asset plus FastAPI Product Server wrapper.

## Implemented Files

- `rules-service/src/main/resources/CampaignStrategy.dmn`
- `api/app/services/kogito_rule_client.py`
- `api/app/services/local_rules.py`
- `api/app/services/rule_service.py`
- `api/app/routes/internal_tools.py`
- `api/app/models/rules.py`

## Current Endpoints

Kogito decision-service endpoint:

```txt
POST /CampaignStrategy/EvaluateCampaignStrategy
```

FastAPI internal tool endpoint:

```txt
POST /internal/tools/evaluate-campaign-strategy
```

No separate friendly rule-service route exists for this decision; Product Server owns the friendly internal-tool path.

## Current Output Shape

FastAPI validates and returns `CampaignStrategyDecision`:

- `rule_decision_id`
- `rule_version`
- `recommended_objective`
- `recommended_cta`
- `kpi_expectation_band`
- `approval_required`
- `segment_constraints`
- `rationale_notes`
- `planning_assumptions`
- `evaluated_at`

Rule decisions are persisted as `RuleDecisionRecord`.
