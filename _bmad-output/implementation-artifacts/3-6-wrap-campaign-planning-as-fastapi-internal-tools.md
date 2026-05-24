# Story 3.6: Wrap Campaign Planning As FastAPI Internal Tools

Status: historical-aligned-summary

## Current Source-Aligned Summary

Product Server wraps campaign planning decisions as internal tools.

Implemented routes:

- `POST /internal/tools/evaluate-campaign-plan`
- `POST /internal/tools/calculate-budget-forecast`
- `POST /internal/tools/recommend-campaign-timeline`

Implemented files:

- `api/app/routes/internal_tools.py`
- `api/app/models/rules.py`
- `api/app/services/rule_service.py`
- `api/app/services/kogito_rule_client.py`
- `api/app/services/local_rules.py`

Current behavior:

- Returns budget bands, daily budget bands, KPI forecast bands, campaign duration, cadence, confidence, assumptions, and estimate disclaimer.
- Persists rule decision records.
