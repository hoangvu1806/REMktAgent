import os


DEFAULT_AGENT_MODEL = "gemini-flash-latest"
DEFAULT_INTERNAL_TOOLS_BASE_URL = "http://127.0.0.1:8000/internal/tools"
DEFAULT_INTERNAL_TOOL_TIMEOUT_SECONDS = 60.0


def get_agent_model() -> str:
    return os.getenv("CONTENT_CREATOR_AGENT_MODEL", DEFAULT_AGENT_MODEL)


def get_internal_tools_base_url() -> str:
    return os.getenv(
        "CONTENT_CREATOR_INTERNAL_TOOLS_BASE_URL",
        DEFAULT_INTERNAL_TOOLS_BASE_URL,
    ).rstrip("/")


def get_internal_tool_timeout_seconds() -> float:
    value = os.getenv("CONTENT_CREATOR_INTERNAL_TOOL_TIMEOUT_SECONDS")
    if value is None:
        return DEFAULT_INTERNAL_TOOL_TIMEOUT_SECONDS
    return float(value)
