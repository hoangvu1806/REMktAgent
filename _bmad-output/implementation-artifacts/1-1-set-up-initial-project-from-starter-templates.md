# Story 1.1: Set Up Initial Project From Starter Templates

Status: historical-aligned-summary

## Current Source-Aligned Summary

This story established the three-service workspace that still exists:

- `web/` - Next.js workbench.
- `api/` - FastAPI Product Server and Agent Server.
- `rules-service/` - Quarkus/Kogito rule-service project.

## Current Runtime

- Web local: `http://localhost:3000`
- Product Server local: `http://127.0.0.1:8282`
- Agent Server local: `http://127.0.0.1:8181`
- Rule Service local: `http://localhost:8080`

## Current Source Layout

Backend:

- `api/app/main.py`
- `api/app/agent_server.py`
- `api/app/routes`
- `api/app/models`
- `api/app/services`
- `api/app/storage`
- `api/app/agents`
- `api/tests`

Rules:

- `rules-service/src/main/resources/CampaignStrategy.dmn`
- `rules-service/src/main/resources/CampaignPlan.dmn`
- `rules-service/src/main/resources/SegmentConstraints.dmn`
- `rules-service/src/main/resources/ClaimRisk.dmn`

## Current Validation Commands

```powershell
cd web
npm run lint
```

```powershell
cd api
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
python -m pytest
```

```powershell
cd rules-service
.\mvnw.cmd test
```

## Notes

Older setup details were removed from this artifact because they no longer match the current source and active BMAD roadmap.
