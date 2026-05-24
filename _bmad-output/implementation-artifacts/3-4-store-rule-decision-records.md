# Story 3.4: Store Rule Decision Records

Status: historical-aligned-summary

## Current Source-Aligned Summary

Rule decision persistence is implemented in SQLite.

Implemented files:

- `api/app/models/rules.py`
- `api/app/services/rule_service.py`
- `api/app/storage/rule_decision_store.py`
- `api/app/routes/internal_tools.py`

Implemented route:

- `GET /internal/tools/rule-decisions/{project_id}`

Persistence:

- `rule_decision_records`

Current behavior:

- Every `RuleService` evaluation stores rule version, input, output, timestamp, decision type, and project ID.
