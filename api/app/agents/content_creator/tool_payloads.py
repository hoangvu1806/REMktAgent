import json
from typing import Any, Literal, TypeAlias, get_args


PropertySegmentInput: TypeAlias = Literal[
    "apartments",
    "land_plots",
    "townhouses",
    "villas_luxury",
    "commercial_real_estate",
]
PROPERTY_SEGMENT_VALUES = get_args(PropertySegmentInput)


def coerce_json_object(
    raw: str | dict[str, Any] | None, *, field_name: str
) -> dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{field_name} must be valid JSON object text") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{field_name} must decode to a JSON object")
    return value


def require_real_project_id(project_id: str) -> str:
    normalized = project_id.strip()
    if not normalized:
        raise RuntimeError("project_id is required before calling internal workflow tools")
    if any(character.isspace() for character in normalized):
        raise RuntimeError(
            "project_id must be the system identifier returned by create_project or get_project, "
            "not a human-readable project name or label."
        )
    if normalized.startswith("placeholder_") or normalized in {
        "project_id",
        "placeholder_project_id",
        "<project_id>",
    }:
        raise RuntimeError(
            "A real project_id is required. Create or load a project first, then call the workflow tool with that project_id."
        )
    return normalized


def require_property_segment(value: str) -> str:
    normalized = value.strip()
    if normalized in PROPERTY_SEGMENT_VALUES:
        return normalized
    raise RuntimeError(
        "property_segment must be one of: "
        + ", ".join(PROPERTY_SEGMENT_VALUES)
        + "."
    )


def require_non_empty(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise RuntimeError(f"{field_name} is required before creating a project")
    return normalized


def require_non_empty_items(values: list[str], *, field_name: str) -> list[str]:
    cleaned = [item.strip() for item in values if item and item.strip()]
    if not cleaned:
        raise RuntimeError(f"{field_name} must include at least one non-empty value")
    return cleaned
