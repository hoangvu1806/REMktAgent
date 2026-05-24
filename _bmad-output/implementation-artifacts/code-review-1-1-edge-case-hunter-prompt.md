# Historical Code Review Prompt: Story 1.1 Edge Case Hunter

Status: historical-aligned-summary

This generated prompt is retained only as review history. Its old file list and assumptions were removed because they no longer match the repository.

Current edge-case review focus:

- Production frontend builds must not fall back to `127.0.0.1` for Agent API.
- Agent Server streaming must survive proxy buffering and timeout settings.
- Agent Server must reach Product Server through `CONTENT_CREATOR_INTERNAL_TOOLS_BASE_URL`.
- Product Server and Rule Service should remain internal for current deployment.
- SQLite path should be writable by the Product Server process.
- `python-dotenv` import must be reflected in dependencies or removed from source.
- Review-state transition must not be called until Product Server draft/review persistence and route support exist.
