---
title: "Product Brief: content_creator"
status: "current-code-aligned"
updated: "2026-05-24"
project_name: content_creator
product_name: AI Real Estate Marketing Workbench
user_name: Vux
primary_channel: Facebook
primary_wedge: in-house real estate marketing teams
public_web: https://mktagent.hoangvu.id.vn
public_agent_api: https://apiagent.hoangvu.id.vn
---

# Product Brief: AI Real Estate Marketing Workbench

## Executive Summary

`content_creator` helps real estate marketers turn a structured project brief into campaign-ready Facebook content with visible reasoning, rule-backed planning, and human review control.

The current product is an MVP prototype. It already has a Next.js workbench, FastAPI Product Server, FastAPI Agent Server, Google ADK multi-agent hierarchy, SQLite MVP persistence for briefs/insights/rule decisions, and Kogito/local deterministic rules. The frontend currently communicates with the Agent Server through streaming chat. Product Server calls from the browser are planned but not wired.

## Problem

Real estate marketing teams repeatedly need to convert project facts, buyer profile, location context, offer details, and campaign objective into usable Facebook posts. Generic AI writing tools can generate copy quickly, but they do not reliably preserve:

- project-specific facts,
- market assumptions,
- campaign objective and CTA logic,
- budget/KPI/timing assumptions,
- segment-specific constraints,
- claim-risk review notes,
- human approval status.

## Target Users

- Primary: in-house real estate marketers preparing Facebook campaign content.
- Secondary: marketing leads reviewing draft quality and claim risk.
- Later: agencies managing repeated client campaign packs.
- Internal: developers/operators validating agent, rule, persistence, and deployment behavior.

## Current Implemented Value

- A desktop workbench captures project brief fields.
- The browser streams a multi-agent response from `POST /agents/chat/stream`.
- ADK agents can create projects, collect partial insight context, call rule-backed planning tools, and generate draft text.
- The UI renders chat, parsed draft cards, a campaign-plan panel, and review controls.
- Product Server persists projects, insight snapshots, market signals, and rule decision records.

## Current Gaps

- Draft cards and review state are not persisted.
- Product Server has no dedicated draft-set, review, or diagnostics routes.
- The frontend does not yet call `NEXT_PUBLIC_API_BASE_URL`.
- Draft review persistence and review-state transition APIs are not implemented; the inactive ADK wrapper has been removed until the backend surface exists.
- The workbench contains mock/static insight examples and heuristic parsing for streamed draft text.

## MVP Scope

In scope now or next:

- Project brief intake.
- Agent-driven research/planning/generation through chat stream.
- Market insight snapshot creation and assumption confirmation.
- Rule-backed campaign strategy, budget/KPI/timing, segment constraints, and claim-risk checks.
- At least three Facebook draft options when agent generation succeeds.
- Human review states in the UI.
- SQLite persistence for MVP state, expanded next to draft/review records.

Out of scope:

- Auth and multi-user workspaces.
- Direct browser access to Kogito.
- Auto-publishing or scheduling.
- CRM automation.
- Paid media bidding optimization.
- Multi-channel generation beyond Facebook.

## Success Criteria

- Marketer can open the workbench, submit a real estate project brief, and receive streamed agent output.
- Generated output includes campaign rationale, draft text, CTA/objective cues, and review notes.
- Rule decisions are deterministic and auditable through Product Server records.
- Public frontend uses `https://apiagent.hoangvu.id.vn`, not local loopback.
- Planned APIs are clearly documented as planned, not implemented.

## Positioning

This is not positioned as a generic AI caption generator. It is a governed AI campaign workbench for real estate Facebook content: agent reasoning plus deterministic rule checks plus human review.
