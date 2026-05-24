# Story 2.4: Edit And Confirm Market Assumptions

Status: historical-aligned-summary

## Current Source-Aligned Summary

Product Server implements assumption update for insight snapshots.

Implemented route:

- `PATCH /projects/{project_id}/insights/{snapshot_id}/assumptions`

Implemented files:

- `api/app/routes/insights.py`
- `api/app/services/insight_service.py`
- `api/app/storage/insight_store.py`

Agent/internal tool support:

- `POST /internal/tools/confirm-market-assumptions`

Current gap:

- Frontend assumption editing is not wired to Product Server yet.
