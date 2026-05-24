# Story 2.1: Trigger Market Insight Collection

Status: historical-aligned-summary

## Current Source-Aligned Summary

Product Server implements market insight snapshot creation and retrieval.

Implemented routes:

- `POST /projects/{project_id}/insights`
- `GET /projects/{project_id}/insights`

Implemented files:

- `api/app/routes/insights.py`
- `api/app/models/insight.py`
- `api/app/services/insight_service.py`
- `api/app/storage/insight_store.py`

Persistence:

- `market_insight_snapshots`
- `market_signals`

Current UI note:

- The frontend insight panel is not yet backed by these Product Server routes.
