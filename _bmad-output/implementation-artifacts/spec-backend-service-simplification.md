---
title: Backend Service Simplification
type: refactor-record
created: 2026-05-20
updated: 2026-05-24
status: historical-aligned-summary
---

# Backend Service Simplification

This artifact records the backend simplification direction after the current source layout changed. It no longer lists removed modules or routes as if they exist.

## Current Backend Layout

- `api/app/main.py` - Product Server.
- `api/app/agent_server.py` - Agent Server.
- `api/app/routes` - health, projects, insights, agents, internal tools, shared response helpers.
- `api/app/models` - Pydantic models for project, insight, rule, and API response contracts.
- `api/app/services` - project, insight, workflow, rule, Kogito adapter, local rule, and signal-building services.
- `api/app/storage` - SQLite base store plus project, insight, and rule decision stores.
- `api/app/agents/content_creator` - Google ADK agent hierarchy and tool wrappers.

## Current Boundary Rules

- Browser currently calls Agent Server `/agents/chat/stream`.
- ADK tool wrappers call Product Server `/internal/tools/*`.
- Product Server owns persistence and rule adapters.
- Rule Service is optional at runtime because `LocalRules` fallback exists.
- Kogito is never called directly by the browser.

## Current Known Gaps

- Draft review persistence and review-state transition API are not implemented; the inactive ADK wrapper has been removed.
- Draft/review persistence is not implemented.
- Diagnostics persistence/routes are not implemented.
- Backend tests need refresh for current ADK tool topology and timeout defaults.

## Current Validation Target

After code changes, use:

```powershell
cd api
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
python -m pytest
```

Current documentation work does not modify source code.
