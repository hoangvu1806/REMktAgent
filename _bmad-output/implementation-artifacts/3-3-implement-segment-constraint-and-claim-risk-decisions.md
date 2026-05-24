# Story 3.3: Implement Segment Constraint and Claim Risk Decisions

Status: historical-review-aligned

## Current Source-Aligned Summary

Segment constraints and claim risk are implemented as Kogito DMN assets plus FastAPI Product Server wrappers.

## Implemented Files

- `rules-service/src/main/resources/SegmentConstraints.dmn`
- `rules-service/src/main/resources/ClaimRisk.dmn`
- `api/app/services/kogito_rule_client.py`
- `api/app/services/local_rules.py`
- `api/app/services/rule_service.py`
- `api/app/routes/internal_tools.py`
- `api/app/models/rules.py`

## Current Endpoints

Kogito decision-service endpoints:

```txt
POST /SegmentConstraints/CheckSegmentConstraints
POST /ClaimRisk/AssessClaimRisk
```

FastAPI internal tool endpoints:

```txt
POST /internal/tools/check-segment-constraints
POST /internal/tools/assess-claim-risk
```

There are no `/rules/segment-constraints` or `/rules/claim-risk` routes in the current source.

## Current Behavior

- Segment constraints return segment-specific guardrail notes.
- Claim risk returns risk flags for sensitive claims such as discount, ownership, handover timing, financing, rental yield, and investment potential.
- Claim risk sets `approval_required` when triggered.
- Rule decisions are persisted as `RuleDecisionRecord`.
