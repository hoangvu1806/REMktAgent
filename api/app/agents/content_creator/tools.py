from typing import Any

import httpx

from .settings import (
    get_internal_tool_timeout_seconds,
    get_internal_tools_base_url,
)
from .tool_payloads import (
    PropertySegmentInput,
    coerce_json_object,
    require_non_empty,
    require_non_empty_items,
    require_property_segment,
    require_real_project_id,
)


def _internal_tool_url(path: str) -> str:
    return f"{get_internal_tools_base_url()}/{path.lstrip('/')}"


def _handle_http_error(path: str, exc: httpx.HTTPError) -> RuntimeError:
    details = ""
    if getattr(exc, "response", None) is not None:
        try:
            details = f" Response body: {exc.response.text}"
        except Exception:
            details = ""
    return RuntimeError(f"Internal tool call failed for {path}: {exc}.{details}")


def _request_internal_tool(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    url = _internal_tool_url(path)
    try:
        timeout = get_internal_tool_timeout_seconds()
        if method.upper() == "POST":
            response = httpx.post(url, json=payload, timeout=timeout)
        elif method.upper() == "GET":
            response = httpx.get(url, timeout=timeout)
        else:
            raise RuntimeError(f"Unsupported internal tool HTTP method: {method}")
        response.raise_for_status()
    except httpx.ConnectError as exc:
        raise RuntimeError(
            "Internal tool endpoint is unreachable. "
            f"Tried {url}. Start the FastAPI app and verify "
            "CONTENT_CREATOR_INTERNAL_TOOLS_BASE_URL points to the running API."
        ) from exc
    except httpx.HTTPError as exc:
        raise _handle_http_error(path, exc) from exc

    body = response.json()
    if not isinstance(body, dict):
        raise RuntimeError(f"Internal tool call returned non-object JSON for {path}")
    return body


def _post_internal_tool(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    return _request_internal_tool("POST", path, payload)


def create_project(
    project_name: str,
    property_segment: PropertySegmentInput,
    location: str,
    price_range: str,
    key_selling_points: list[str],
    campaign_objective: str,
    buyer_profile: str,
    tone: str,
    promotion_details: str | None = None,
) -> dict[str, Any]:
    """Create a project brief through the FastAPI product boundary.
    property_segment is a function-calling enum. Infer the best enum from the
    user's natural-language segment description before calling; do not pass the
    user's display label.
    """
    return _post_internal_tool(
        "create-project",
        {
            "project_name": require_non_empty(project_name, field_name="project_name"),
            "property_segment": require_property_segment(property_segment),
            "location": require_non_empty(location, field_name="location"),
            "price_range": require_non_empty(price_range, field_name="price_range"),
            "key_selling_points": require_non_empty_items(
                key_selling_points,
                field_name="key_selling_points",
            ),
            "campaign_objective": require_non_empty(
                campaign_objective,
                field_name="campaign_objective",
            ),
            "buyer_profile": require_non_empty(
                buyer_profile,
                field_name="buyer_profile",
            ),
            "tone": require_non_empty(tone, field_name="tone"),
            "promotion_details": promotion_details.strip() if promotion_details else None,
        },
    )


def update_project(
    project_id: str,
    project_name: str,
    property_segment: PropertySegmentInput,
    location: str,
    price_range: str,
    key_selling_points: list[str],
    campaign_objective: str,
    buyer_profile: str,
    tone: str,
    promotion_details: str | None = None,
) -> dict[str, Any]:
    """Update a saved project brief after the user clarifies intake details."""
    return _post_internal_tool(
        "update-project",
        {
            "project_id": require_real_project_id(project_id),
            "project_name": require_non_empty(project_name, field_name="project_name"),
            "property_segment": require_property_segment(property_segment),
            "location": require_non_empty(location, field_name="location"),
            "price_range": require_non_empty(price_range, field_name="price_range"),
            "key_selling_points": require_non_empty_items(
                key_selling_points,
                field_name="key_selling_points",
            ),
            "campaign_objective": require_non_empty(
                campaign_objective,
                field_name="campaign_objective",
            ),
            "buyer_profile": require_non_empty(
                buyer_profile,
                field_name="buyer_profile",
            ),
            "tone": require_non_empty(tone, field_name="tone"),
            "promotion_details": promotion_details.strip() if promotion_details else None,
        },
    )


def get_project(project_id: str) -> dict[str, Any]:
    """Load an existing project before running insight or planning workflows."""
    project_id = require_real_project_id(project_id)
    return _request_internal_tool("GET", f"get-project/{project_id}")


def collect_insight_workflow(
    project_id: str,
    approved_source_ids: list[str] | None = None,
    user_context: str | None = None,
    official_project_url: str | None = None,
    user_material_refs: list[str] | None = None,
) -> dict[str, Any]:
    """
    project_id must be the system identifier returned by create_project or
    get_project, not the project name.
    """
    return _post_internal_tool(
        "collect-insight-workflow",
        {
            "project_id": require_real_project_id(project_id),
            "approved_source_ids": approved_source_ids or [],
            "user_context": user_context,
            "official_project_url": official_project_url,
            "user_material_refs": user_material_refs or [],
        },
    )


def confirm_market_assumptions(
    project_id: str,
    insight_snapshot_id: str,
    assumptions_json: str = "{}",
    confirmed: bool = True,
) -> dict[str, Any]:
    """Confirm or revise insight assumptions before Kogito planning.

    assumptions_json is optional JSON object text:
    {"assumptions":[{"question":"...","answer":"..."}]}.
    """
    assumptions_payload = coerce_json_object(
        assumptions_json,
        field_name="assumptions_json",
    )
    return _post_internal_tool(
        "confirm-market-assumptions",
        {
            "project_id": require_real_project_id(project_id),
            "insight_snapshot_id": require_non_empty(
                insight_snapshot_id,
                field_name="insight_snapshot_id",
            ),
            "assumptions": assumptions_payload.get("assumptions", []),
            "confirmed": confirmed,
        },
    )

def collect_project_facts(
    project_id: str,
    brief_json: str,
    user_material_refs: list[str] | None = None,
    official_project_url: str | None = None,
) -> dict[str, Any]:
    """Collect user-provided and official project facts through FastAPI tools."""
    return _post_internal_tool(
        "collect-project-facts",
        {
            "project_id": require_real_project_id(project_id),
            "brief": coerce_json_object(brief_json, field_name="brief_json"),
            "user_material_refs": user_material_refs or [],
            "official_project_url": official_project_url,
        },
    )


def prepare_campaign_context(
    project_id: str,
    insight_summary: str,
    insight_snapshot_id: str | None = None,
    planning_constraints_json: str | None = None,
    unavailable_signals: list[str] | None = None,
) -> dict[str, Any]:
    """Run the Epic 3 planning workflow through the FastAPI product boundary."""
    return _post_internal_tool(
        "prepare-campaign-context",
        {
            "project_id": require_real_project_id(project_id),
            "insight_summary": insight_summary,
            "insight_snapshot_id": insight_snapshot_id,
            "planning_constraints": coerce_json_object(
                planning_constraints_json,
                field_name="planning_constraints_json",
            ),
            "unavailable_signals": unavailable_signals or [],
        },
    )


def evaluate_campaign_strategy(
    project_id: str,
    brief_json: str,
    insight_snapshot_id: str | None = None,
    insight_summary: str | None = None,
) -> dict[str, Any]:
    """Evaluate campaign strategy through the Kogito-backed FastAPI tool boundary."""
    return _post_internal_tool(
        "evaluate-campaign-strategy",
        {
            "project_id": require_real_project_id(project_id),
            "brief": coerce_json_object(brief_json, field_name="brief_json"),
            "insight_snapshot_id": insight_snapshot_id,
            "insight_summary": insight_summary,
        },
    )


def evaluate_campaign_plan(
    project_id: str,
    brief_json: str,
    insight_snapshot_id: str | None = None,
    insight_summary: str | None = None,
    planning_constraints_json: str | None = None,
    unavailable_signals: list[str] | None = None,
) -> dict[str, Any]:
    """Evaluate campaign plan metrics through Kogito-backed FastAPI tools."""
    return _post_internal_tool(
        "evaluate-campaign-plan",
        {
            "project_id": require_real_project_id(project_id),
            "brief": coerce_json_object(brief_json, field_name="brief_json"),
            "insight_snapshot_id": insight_snapshot_id,
            "insight_summary": insight_summary,
            "planning_constraints": coerce_json_object(
                planning_constraints_json,
                field_name="planning_constraints_json",
            ),
            "unavailable_signals": unavailable_signals or [],
        },
    )


def calculate_budget_forecast(
    project_id: str,
    campaign_plan_inputs_json: str,
) -> dict[str, Any]:
    """Calculate budget and KPI forecast bands through FastAPI internal tools."""
    return _post_internal_tool(
        "calculate-budget-forecast",
        {
            "project_id": require_real_project_id(project_id),
            "campaign_plan_inputs": coerce_json_object(
                campaign_plan_inputs_json,
                field_name="campaign_plan_inputs_json",
            ),
        },
    )


def recommend_campaign_timeline(
    project_id: str,
    campaign_plan_inputs_json: str,
) -> dict[str, Any]:
    """Recommend campaign duration and cadence through FastAPI internal tools."""
    return _post_internal_tool(
        "recommend-campaign-timeline",
        {
            "project_id": require_real_project_id(project_id),
            "campaign_plan_inputs": coerce_json_object(
                campaign_plan_inputs_json,
                field_name="campaign_plan_inputs_json",
            ),
        },
    )


def check_segment_constraints(
    project_id: str,
    property_segment: str,
    draft_context_json: str,
) -> dict[str, Any]:
    """Check segment-specific content constraints through FastAPI internal tools."""
    return _post_internal_tool(
        "check-segment-constraints",
        {
            "project_id": require_real_project_id(project_id),
            "property_segment": property_segment,
            "draft_context": coerce_json_object(
                draft_context_json,
                field_name="draft_context_json",
            ),
        },
    )


def assess_claim_risk(
    project_id: str,
    draft_text: str,
    project_facts_json: str,
) -> dict[str, Any]:
    """Assess risk-sensitive real estate claims through FastAPI internal tools."""
    return _post_internal_tool(
        "assess-claim-risk",
        {
            "project_id": require_real_project_id(project_id),
            "draft_text": draft_text,
            "project_facts": coerce_json_object(
                project_facts_json,
                field_name="project_facts_json",
            ),
        },
    )

