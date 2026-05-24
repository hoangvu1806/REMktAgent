# Story 2.3: Display Market Insight Snapshot Panel

Status: historical-aligned-summary

## Current Source-Aligned Summary

The frontend contains an Insights view in `ProjectBriefWorkbench`.

Current behavior:

- Shows insight-style items in the workbench.
- Uses local/mock data and streamed text handling.
- Does not load persisted `MarketInsightSnapshot` rows from Product Server yet.

Backend support exists through:

- `GET /projects/{project_id}/insights`
- `POST /projects/{project_id}/insights`

Current gap:

- Wire frontend to Product Server insight routes and remove mock-only assumptions from the UI.
