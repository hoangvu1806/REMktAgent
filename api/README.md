# content_creator API

FastAPI backend for the Product Server and Agent Server.

## Services

| App | Entrypoint | Local port | Purpose |
|---|---|---:|---|
| Product Server | `app.main:app` | `8282` | Product routes, internal ADK tools, Kogito/local rule wrappers |
| Agent Server | `app.agent_server:app` | `8181` | Browser-facing Google ADK SSE chat stream |

Both apps currently use permissive CORS:

```py
allow_origins=["*"]
allow_credentials=False
```

## Local Run

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run Product Server:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8282
```

Run Agent Server in another terminal:

```powershell
uvicorn app.agent_server:app --reload --host 127.0.0.1 --port 8181
```

OpenAPI docs:

- Product Server: `http://127.0.0.1:8282/docs`
- Agent Server: `http://127.0.0.1:8181/docs`

## Environment

Important variables:

| Variable | Used by | Current meaning |
|---|---|---|
| `GOOGLE_API_KEY` or `GEMINI_API_KEY` | Agent Server | Google ADK/Gemini auth |
| `CONTENT_CREATOR_AGENT_MODEL` | Agent Server | ADK agent model, e.g. `gemini-2.5-flash` |
| `CONTENT_CREATOR_INTERNAL_TOOLS_BASE_URL` | Agent tools | Product Server internal tool base, normally `http://127.0.0.1:8282/internal/tools` |
| `CONTENT_CREATOR_INTERNAL_TOOL_TIMEOUT_SECONDS` | Agent tools | HTTP timeout for internal tool calls |
| `KOGITO_RULE_SERVICE_URL` | Product Server | Optional Kogito base URL. If unset, local deterministic rules are used |
| `KOGITO_RULE_TIMEOUT_SECONDS` | Product Server | Kogito HTTP timeout |
| `SQLITE_DATABASE_PATH` | Product Server | SQLite file path |
| `ADK_DISABLE_PROGRESSIVE_SSE_STREAMING` | Agent runtime | ADK/Gemini streaming behavior flag |

Do not commit real `.env` secrets.

## Product Routes

Implemented in `app.main:app`:

- `GET /health`
- `POST /projects`
- `GET /projects/{project_id}`
- `PUT /projects/{project_id}`
- `POST /projects/{project_id}/insights`
- `GET /projects/{project_id}/insights`
- `PATCH /projects/{project_id}/insights/{snapshot_id}/assumptions`

Successful responses use:

```json
{ "data": {}, "meta": { "correlation_id": "..." } }
```

Recoverable errors use:

```json
{ "error": { "code": "...", "message": "...", "details": {}, "recoverable": true }, "meta": { "correlation_id": "..." } }
```

## Agent Route

Implemented in `app.agent_server:app`:

- `POST /agents/chat/stream`

Request:

```json
{
  "user_id": "default_user",
  "session_id": "session-id",
  "message": "user message or brief summary"
}
```

Response is `text/event-stream`. Events are emitted as:

```txt
data: {"author":"...","type":"agent_event","partial":false,"text":"..."}

data: [DONE]
```

Sessions are in-memory. Restarting the Agent Server clears conversation sessions.

## Internal Tool Routes

Implemented under `/internal/tools`:

- `POST /collect-project-facts`
- `POST /create-project`
- `POST /update-project`
- `GET /get-project/{project_id}`
- `POST /collect-insight-workflow`
- `POST /confirm-market-assumptions`
- `POST /prepare-campaign-context`
- `POST /evaluate-campaign-strategy`
- `POST /evaluate-campaign-plan`
- `POST /calculate-budget-forecast`
- `POST /recommend-campaign-timeline`
- `POST /check-segment-constraints`
- `POST /assess-claim-risk`
- `GET /rule-decisions/{project_id}`

Current gap: draft review state transition is not implemented yet. There is no active ADK review-state tool wrapper until Product Server draft/review persistence exists.

## Persistence

SQLite stores:

- `projects`
- `project_briefs`
- `market_insight_snapshots`
- `market_signals`
- `rule_decision_records`

Draft sets, draft review decisions, and diagnostics events are not persisted yet.

## Tests

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
python -m pytest
```

Current known drift: the test suite has stale expectations around the default internal tool timeout and some ADK tool object behavior. Treat failures there as test/doc alignment work unless code behavior is being changed intentionally.
