# Story 1.4: Validate Required And Low-Specificity Brief Fields

Status: historical-aligned-summary

## Current Source-Aligned Summary

The workbench contains client-side brief readiness and validation behavior inside:

- `web/src/components/features/project-brief/project-brief-workbench.tsx`

Current behavior:

- Required project brief fields are represented in the UI.
- The user can improve brief values before triggering the agent stream.
- Validation/readiness is frontend-local.

Current gap:

- Product Server does not yet receive frontend save/update calls for brief validation state.
