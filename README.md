# Real estate marketing workbench

For turning a structured project brief into Facebook campaign content. The current implementation is an MVP prototype with a Next.js workbench, FastAPI services, Google ADK agents, and Kogito/DMN rules.

## Architecture

```text
Browser
  -> Next.js Web app
    -> FastAPI Agent Server
      -> Google ADK agents
        -> FastAPI Product Server internal tools
          -> SQLite
          -> Kogito Rule Service
```

| Service | Local URL | Entrypoint | Purpose |
|---|---|---|---|
| Web | `http://localhost:3000` | `web/` | Workbench UI at `/` and `/projects/new` |
| Agent Server | `http://127.0.0.1:8181` | `api/app/agent_server.py` | Browser-facing ADK streaming endpoint |
| Product Server | `http://127.0.0.1:8282` | `api/app/main.py` | Product APIs, internal tools, persistence, rule wrappers |
| Rule Service | `http://localhost:8080` | `rules-service/` | Optional Kogito DMN decision runtime |

## Repository Layout

```text
api/            FastAPI Product Server, FastAPI Agent Server, ADK agents, tests
web/            Next.js workbench UI
rules-service/  Quarkus/Kogito DMN rule service
docs/           Project context and rule documentation
_bmad-output/   BMAD planning and implementation artifacts
```

## Prerequisites

- Node.js 20+
- Python 3.11+
- Java 17+
- Maven, or the included `rules-service/mvnw.cmd`
- Google API key for ADK/Gemini agent execution

## Environment Setup

Create local environment files:

```powershell
Copy-Item .env.example .env
Copy-Item web/.env.example web/.env.local
Copy-Item api/.env.example api/.env
```

Set at least one Google credential in `api/.env`:

```env
GOOGLE_API_KEY=your-google-api-key
# or
GEMINI_API_KEY=your-gemini-api-key
```

Recommended local frontend values:

```env
NEXT_PUBLIC_AGENT_API_BASE_URL=http://127.0.0.1:8181
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8282
```

Important backend values:

```env
CONTENT_CREATOR_INTERNAL_TOOLS_BASE_URL=http://127.0.0.1:8282/internal/tools
CONTENT_CREATOR_INTERNAL_TOOL_TIMEOUT_SECONDS=60
SQLITE_DATABASE_PATH=./data/content_creator.sqlite3
CONTENT_CREATOR_AGENT_MODEL=gemini-2.5-flash
KOGITO_RULE_SERVICE_URL=http://localhost:8080
```

If `KOGITO_RULE_SERVICE_URL` is not configured or the Rule Service is unavailable, the Product Server uses local deterministic rule fallback logic.

## Run Locally

Use three terminals for the main MVP flow.

### 1. Start the Product Server

```powershell
cd api
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8282
```

OpenAPI docs:

```text
http://127.0.0.1:8282/docs
```

### 2. Start the Agent Server

```powershell
cd api
python -m uvicorn app.agent_server:app --reload --host 127.0.0.1 --port 8181
```

OpenAPI docs:

```text
http://127.0.0.1:8181/docs
```

### 3. Start the Web App

```powershell
cd web
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

## Run with Docker Compose

Use Docker Compose when you want to start the whole stack with one command.

Set a Google credential in your shell or in a local root `.env` file:

```env
GOOGLE_API_KEY=your-google-api-key
# or
GEMINI_API_KEY=your-gemini-api-key
```

Start everything:

```powershell
docker compose up --build
```

Services:

| Service | URL |
|---|---|
| Web | `http://localhost:3000` |
| Agent Server | `http://127.0.0.1:8181/docs` |
| Product Server | `http://127.0.0.1:8282/docs` |
| Rule Service | `http://localhost:8080` |

Stop the stack:

```powershell
docker compose down
```

Remove the persisted SQLite Docker volume:

```powershell
docker compose down -v
```

## Optional: Run the Rule Service

The app can run without Kogito because the Product Server has local rule fallback logic. Start Kogito only when you want to exercise the DMN runtime.

```powershell
cd rules-service
mvn quarkus:dev
```

Rule Service URL:

```text
http://localhost:8080
```

## Usage

1. Open `http://localhost:3000`.
2. Fill in the project brief fields.
3. Click `Bắt đầu tạo bài viết bằng AI`.
4. The frontend streams responses from the Agent Server.
5. The Agent Server coordinates ADK agents and calls Product Server internal tools.
6. Review generated insights, draft content, campaign planning, and local review status in the workbench.

Current UI state for drafts/review is mostly local React state. Persisted draft sets, persisted draft review decisions, diagnostics events, auth, publishing, CRM, and analytics are not implemented yet.

## API Summary

Product Server routes:

- `GET /health`
- `POST /projects`
- `GET /projects/{project_id}`
- `PUT /projects/{project_id}`
- `POST /projects/{project_id}/insights`
- `GET /projects/{project_id}/insights`
- `PATCH /projects/{project_id}/insights/{snapshot_id}/assumptions`

Agent Server route:

- `POST /agents/chat/stream`

Internal tool routes:

- `POST /internal/tools/collect-project-facts`
- `POST /internal/tools/create-project`
- `POST /internal/tools/update-project`
- `GET /internal/tools/get-project/{project_id}`
- `POST /internal/tools/collect-insight-workflow`
- `POST /internal/tools/confirm-market-assumptions`
- `POST /internal/tools/prepare-campaign-context`
- `POST /internal/tools/evaluate-campaign-strategy`
- `POST /internal/tools/evaluate-campaign-plan`
- `POST /internal/tools/calculate-budget-forecast`
- `POST /internal/tools/recommend-campaign-timeline`
- `POST /internal/tools/check-segment-constraints`
- `POST /internal/tools/assess-claim-risk`
- `GET /internal/tools/rule-decisions/{project_id}`

## Deployment Notes

Current public deployment expects:

| Service | Public URL |
|---|---|
| Web | `https://mktagent.hoangvu.id.vn` |
| Agent Server | `https://apiagent.hoangvu.id.vn` |
| Product Server | internal only |
| Rule Service | internal only |

Set the web build environment:

```env
NEXT_PUBLIC_AGENT_API_BASE_URL=https://apiagent.hoangvu.id.vn
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8282
```

Keep the Product Server and Rule Service private if the Agent Server can reach them internally. Ensure the reverse proxy for the Agent Server supports long-lived streaming POST responses and does not buffer `text/event-stream`.

## Testing

Frontend:

```powershell
cd web
npm run lint
```

Backend:

```powershell
cd api
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
python -m pytest
```

Rules service:

```powershell
cd rules-service
mvn test
```

## Troubleshooting

- Agent Server cannot call tools: verify `CONTENT_CREATOR_INTERNAL_TOOLS_BASE_URL` and that the Product Server is running.
- Browser cannot stream responses: verify `NEXT_PUBLIC_AGENT_API_BASE_URL`, CORS/proxy settings, and that the proxy does not buffer streaming responses.
- Docker web cannot reach the Agent Server from the browser: rebuild with `NEXT_PUBLIC_AGENT_API_BASE_URL` pointing to the browser-accessible Agent Server URL, usually `http://127.0.0.1:8181` for local Docker.
- Kogito unavailable: unset `KOGITO_RULE_SERVICE_URL` or start `rules-service`; local rule fallback is available.
- Lost chat context after restart: Agent Server sessions are currently in memory.

## Current Limitations

- Browser does not call Product Server directly yet.
- Draft sets and review decisions are not persisted.
- Diagnostics APIs/events are not implemented.
- Auth, RBAC, multi-user workspaces, queues, publishing, CRM, and analytics are out of scope for the current MVP.
