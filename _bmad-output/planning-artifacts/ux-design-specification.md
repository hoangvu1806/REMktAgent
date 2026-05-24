---
workflowType: ux-design
status: current-code-aligned
project_name: content_creator
product_name: AI Real Estate Marketing Workbench
user_name: Vux
date: 2026-05-24
---

# UX Design Specification

## Current UX

The current frontend is a desktop-oriented workbench rendered by `ProjectBriefWorkbench`.

Routes:

- `/`
- `/projects/new`

Both routes show the same workbench.

## Layout Model

The UI uses a two-column operational workbench:

- Brief/chat area for project input and streamed agent responses.
- Workflow canvas for `Brief`, `Insights`, `Drafts`, and `Review` views.

This is not a marketing landing page. The first screen is the actual working interface.

## Current Views

### Brief

Purpose: capture real estate project context.

Fields:

- project name,
- property segment,
- location,
- price range,
- key selling points,
- campaign objective,
- buyer profile,
- tone,
- promotion details.

Current behavior:

- Stored in React state.
- Sent to Agent Server as a generated brief summary.

### Insights

Purpose: show market/context signals and assumptions.

Current behavior:

- Contains static/mock insight items plus live updates from streamed agent text where applicable.
- Not loaded from Product Server in current frontend.

### Drafts

Purpose: compare generated Facebook draft candidates.

Current behavior:

- Draft cards are created from parsed streamed text or local mock defaults.
- Draft copy can be copied.
- Draft statuses can be changed locally.
- Drafts are not persisted.

### Review

Purpose: review draft risk notes and campaign-plan-like metrics.

Current behavior:

- Campaign plan data is parsed heuristically from streamed text.
- Review status and risk display are local UI state.
- Product Server review persistence is not implemented.

## UX Principles

- Keep the user inside the workbench; avoid separate landing or wizard pages.
- Make agent progress visible through streaming text and step state.
- Keep human approval explicit; generated drafts are not final.
- Distinguish source-backed, user-provided, and unavailable insight states where possible.
- Do not show raw Kogito payloads to marketers.
- Keep diagnostics separate from the main marketer workflow when implemented.

## Current UX Gaps

- Saved state is incomplete because Product Server is not used by frontend.
- Draft review state is local only.
- Insight display includes mock examples.
- There is no persisted diagnostics view.
- User identity is hardcoded to `default_user`.
- Agent session IDs are client-generated and not durable.

## Required Next UX Changes

1. Persist project brief state through Product Server.
2. Replace mock insight panel data with Product Server insight snapshots.
3. Persist draft sets and review state.
4. Add explicit loading/error states for Product Server failures.
5. Add internal diagnostics view after diagnostics API exists.
6. Keep public deployment env visible in deployment docs, not in UI text.
