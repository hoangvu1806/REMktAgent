# content_creator web

Next.js workbench UI for the real estate marketing content workflow.

## Stack

- Next.js App Router 16
- React 19
- TypeScript
- Tailwind CSS 4
- `lucide-react`
- `react-markdown`
- shadcn-style local component setup

## Current Screens

- `/`
- `/projects/new`

Both routes render `ProjectBriefWorkbench`.

## Runtime API Calls

The current frontend uses `web/src/lib/api.ts`.

Implemented browser call:

```txt
POST {NEXT_PUBLIC_AGENT_API_BASE_URL}/agents/chat/stream
```

Default fallback in code:

```env
NEXT_PUBLIC_AGENT_API_BASE_URL=http://127.0.0.1:8181
```

Current deployment value:

```env
NEXT_PUBLIC_AGENT_API_BASE_URL=https://apiagent.hoangvu.id.vn
```

`NEXT_PUBLIC_API_BASE_URL` is configured for the Product Server but is not currently used by `web/src`.

## Current UX Behavior

- The workbench captures a structured project brief.
- It sends brief/user messages to the Agent Server through XHR-based SSE streaming.
- It renders streaming agent text in the chat panel.
- It parses streamed text heuristically into draft cards and campaign plan fields.
- Insight, draft, review, and plan panels are currently client-side UI state. They are not persisted through Product Server draft/review APIs yet.
- Draft status changes are local React state only.

## Local Run

```powershell
npm install
npm run dev
```

Default local URL:

```txt
http://localhost:3000
```

## Public Deployment

Before build/redeploy, set:

```env
NEXT_PUBLIC_AGENT_API_BASE_URL=https://apiagent.hoangvu.id.vn
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8282
```

Because `NEXT_PUBLIC_*` variables are embedded at build time, restart the dev server or rebuild/redeploy after changing them.

## Validation

```powershell
npm run lint
```

## Scope Boundary

Current browser-facing backend boundary is the Agent Server. Product Server calls from the browser are planned but not wired in current code. The browser must not call Kogito directly.
