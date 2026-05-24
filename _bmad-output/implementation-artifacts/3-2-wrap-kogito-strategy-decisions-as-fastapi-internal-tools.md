# Story 3.2: Wrap Strategy Decisions As FastAPI Internal Tools

Status: historical-aligned-summary

## Current Source-Aligned Summary

Product Server wraps campaign strategy rule evaluation as an internal tool.

Implemented route:

- `POST /internal/tools/evaluate-campaign-strategy`

Implemented files:

- `api/app/routes/internal_tools.py`
- `api/app/models/rules.py`
- `api/app/services/rule_service.py`
- `api/app/services/kogito_rule_client.py`
- `api/app/services/local_rules.py`

Current behavior:

- Uses Kogito when configured.
- Uses Python local rules when Kogito URL is unset.
- Persists `RuleDecisionRecord`.
