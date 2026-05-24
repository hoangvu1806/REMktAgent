---
workflowType: brainstorming
status: current-code-aligned-summary
project_name: content_creator
user_name: Vux
date: 2026-05-24
supersedes_original_date: 2026-05-18
---

# Brainstorming Summary

This artifact is retained as a compact record. The original brainstorming session contained pre-implementation options that no longer match the codebase. Current planning should use the active BMAD documents.

## Current Product Direction

Build a real estate Facebook campaign workbench that combines:

- structured project brief intake,
- streamed ADK agent reasoning,
- rule-backed planning and safety decisions,
- human review controls,
- lightweight persistence.

## Current Architecture Direction

The implemented runtime is:

```text
Browser -> Web -> Agent Server -> ADK agents -> Product Server internal tools -> SQLite/rules
```

The browser currently calls the Agent Server directly. Product Server browser integration is backlog.

## Current UX Direction

The current UI is a desktop workbench with four views:

- Brief
- Insights
- Drafts
- Review

The next UX improvement is replacing mock/local-only state with Product Server-backed project, insight, draft, and review state.

## Current Implementation Questions

1. Should review-state transition be implemented now or kept out of the agent tool list until draft/review persistence exists?
2. What draft/review schema should be persisted first?
3. Should frontend save brief/insight state before or after draft persistence is added?
4. What minimal diagnostics view is useful before durable sessions exist?
