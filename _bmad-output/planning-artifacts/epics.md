---
workflowType: epics
status: current-code-aligned
project_name: content_creator
user_name: Vux
date: 2026-05-24
---

# Epics And Stories

This replaces the older six-epic plan with a smaller code-aligned roadmap. Historical story files under `_bmad-output/implementation-artifacts/` remain useful as implementation history, but this file is the active epic source of truth.

## Epic 1: Runtime And Deployment Alignment

Goal: keep local and public runtime configuration consistent with source.

Status: mostly done.

### Story 1.1: Align Local Ports And Env Templates

As a developer, I want env examples to match current service ports, so local setup and deployment do not drift.

Acceptance:

- Product Server uses `8282`.
- Agent Server uses `8181`.
- Frontend public agent URL is `https://apiagent.hoangvu.id.vn`.
- `CONTENT_CREATOR_INTERNAL_TOOLS_BASE_URL` points to Product Server `/internal/tools`.

### Story 1.2: Document Current Public Exposure

As an operator, I want docs to show that only web and Agent Server need public exposure for current UI.

Acceptance:

- Docs show web at `https://mktagent.hoangvu.id.vn`.
- Docs show Agent API at `https://apiagent.hoangvu.id.vn`.
- Docs show Product Server and Rule Service as internal/private.

## Epic 2: Project Brief And Insight State

Goal: preserve project brief and insight state through Product Server.

Status: backend implemented, frontend integration partial/missing.

### Story 2.1: Product Project CRUD

Implemented.

Acceptance:

- `POST /projects` creates a project.
- `GET /projects/{project_id}` retrieves it.
- `PUT /projects/{project_id}` updates it.
- SQLite persists project and brief data.

### Story 2.2: Market Insight Snapshot API

Implemented.

Acceptance:

- `POST /projects/{project_id}/insights` creates a snapshot.
- `GET /projects/{project_id}/insights` lists snapshots.
- `PATCH /projects/{project_id}/insights/{snapshot_id}/assumptions` updates assumptions.
- SQLite persists snapshots and signals.

### Story 2.3: Frontend Product API Integration

Backlog.

Acceptance:

- Workbench saves project briefs through Product Server.
- Workbench loads saved project state.
- Workbench does not rely only on local React state for project/insight state.

## Epic 3: Agent Streaming Workflow

Goal: support a browser-facing ADK stream that can call Product Server internal tools.

Status: implemented with known limitations.

### Story 3.1: Agent Server SSE Chat

Implemented.

Acceptance:

- `POST /agents/chat/stream` emits `agent_event` chunks and `[DONE]`.
- Browser uses `NEXT_PUBLIC_AGENT_API_BASE_URL`.
- Streaming responses disable proxy buffering where supported.

### Story 3.2: ADK Agent Hierarchy

Implemented.

Acceptance:

- Root agent routes to intake, research, planning, and generation/governance managers.
- Internal tool wrappers call Product Server.
- Research search specialists use ADK `google_search`.

### Story 3.3: Durable Session Boundary

Backlog.

Acceptance:

- Sessions can survive Agent Server restart or the docs explicitly keep volatile sessions as an accepted prototype constraint.

## Epic 4: Rule-Backed Planning And Safety

Goal: provide deterministic campaign strategy, planning, segment guardrail, and claim-risk decisions.

Status: implemented with parity review needed.

### Story 4.1: Kogito DMN Assets

Implemented.

Acceptance:

- DMNs exist for campaign strategy, campaign plan, segment constraints, and claim risk.
- Quarkus/Kogito exposes generated decision-service endpoints.

### Story 4.2: FastAPI Rule Wrappers And Audit Records

Implemented.

Acceptance:

- Product Server exposes internal rule tools.
- Rule responses are validated by Pydantic.
- Rule decision records are persisted.
- `LocalRules` fallback works when Kogito URL is unset.

### Story 4.3: LocalRules/DMN Parity Review

Backlog.

Acceptance:

- Document and test any intentional differences between Kogito and `LocalRules`.
- Fix accidental divergence in fallback logic.

## Epic 5: Draft And Review Persistence

Goal: turn streamed draft-like UI output into persisted product data.

Status: backlog.

### Story 5.1: Implement Draft Set Models And Storage

Acceptance:

- Persist draft set linked to project, insight snapshot, and rule decisions.
- Persist each draft candidate with caption, angle, format, persona, CTA, objective, creative suggestion, review notes, and risk notes.

### Story 5.2: Implement Draft Routes

Acceptance:

- API can create/list draft sets for a project.
- API validates generated draft structure before persistence.

### Story 5.3: Implement Review State Route

Acceptance:

- Acceptance target: add draft/review persistence and reintroduce review-state transition tooling only after the Product Server route exists.
- Review state can be changed to generated, needs edit, approved, or rejected.
- Review notes are persisted.

### Story 5.4: Wire Frontend Draft/Review API

Acceptance:

- Workbench loads persisted drafts.
- Review buttons update Product Server, not only React state.

## Epic 6: Diagnostics And Test Alignment

Goal: make the system debuggable and test expectations current.

Status: backlog.

### Story 6.1: Diagnostics API

Acceptance:

- Planned diagnostics API exposes project diagnostics: insight snapshots, rule decisions, draft counts, generation status, and error categories.

### Story 6.2: Dependency Hygiene

Acceptance:

- Backend requirements include every directly imported package, including `python-dotenv`.

### Story 6.3: Test Suite Alignment

Acceptance:

- Backend tests reflect current ADK `AgentTool` usage and current timeout defaults.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest` passes in a fresh backend environment.

### Story 6.4: Documentation Gate

Acceptance:

- README, PRD, Architecture, Epics, UX, sprint status, and DMN docs distinguish implemented behavior from backlog.
