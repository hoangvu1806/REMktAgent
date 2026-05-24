import httpx
import pytest
from google.adk.tools.function_tool import FunctionTool

from app.agents import tools
from app.agents.content_creator.tool_payloads import (
    require_property_segment,
    require_real_project_id,
)


class _FakeResponse:
    def __init__(self, payload: dict[str, object], status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("POST", "http://testserver/internal/tools/fail")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError("failed", request=request, response=response)

    def json(self) -> dict[str, object]:
        return self._payload


def test_strategy_and_risk_tools_post_expected_payloads(monkeypatch) -> None:
    calls: list[tuple[str, dict[str, object]]] = []

    def fake_post(url: str, json: dict[str, object], timeout: float) -> _FakeResponse:
        calls.append((url, json))
        return _FakeResponse({"data": {"ok": True}})

    monkeypatch.setenv("CONTENT_CREATOR_INTERNAL_TOOLS_BASE_URL", "http://api/internal/tools/")
    monkeypatch.setattr(tools.httpx, "post", fake_post)

    tools.evaluate_campaign_strategy(
        project_id="project-1",
        brief_json='{"property_segment":"apartments"}',
        insight_snapshot_id="snapshot-1",
        insight_summary="Summary",
    )
    tools.evaluate_campaign_plan(
        project_id="project-1",
        brief_json='{"property_segment":"apartments"}',
        insight_snapshot_id="snapshot-1",
        insight_summary="Summary",
        planning_constraints_json='{"budget_constraint":"50M VND"}',
        unavailable_signals=["competitor budget benchmark"],
    )
    tools.calculate_budget_forecast(
        project_id="project-1",
        campaign_plan_inputs_json='{"lead_target":120,"campaign_duration_days":21}',
    )
    tools.recommend_campaign_timeline(
        project_id="project-1",
        campaign_plan_inputs_json='{"objective":"lead_generation","segment":"apartments"}',
    )
    tools.collect_project_facts(
        project_id="project-1",
        brief_json='{"project_name":"Sunrise Riverside"}',
        user_material_refs=["sales-kit.pdf"],
        official_project_url="https://example.com/project",
    )
    tools.check_segment_constraints(
        project_id="project-1",
        property_segment="apartments",
        draft_context_json='{"format_type":"benefit_led"}',
    )
    tools.assess_claim_risk(
        project_id="project-1",
        draft_text="Guaranteed rental yield",
        project_facts_json='{"location":"Thu Duc"}',
    )
    tools.collect_insight_workflow(
        project_id="project-1",
        user_context="Metro demand context",
        official_project_url="https://example.com/project",
        user_material_refs=["sales-kit.pdf"],
    )
    tools.create_project(
        project_name="Sunrise Riverside",
        property_segment="apartments",
        location="Thu Duc, Ho Chi Minh City",
        price_range="3-5B VND",
        key_selling_points=["near metro", "river view"],
        campaign_objective="lead_generation",
        buyer_profile="young families",
        tone="professional_trustworthy",
        promotion_details="limited booking incentive",
    )
    tools.prepare_campaign_context(
        project_id="project-1",
        insight_summary="Verified local planning and buyer demand context.",
        insight_snapshot_id="snapshot-1",
        planning_constraints_json='{"total_budget_vnd":120000000}',
        unavailable_signals=["competitor budget benchmark"],
    )

    assert calls == [
        (
            "http://api/internal/tools/evaluate-campaign-strategy",
            {
                "project_id": "project-1",
                "brief": {"property_segment": "apartments"},
                "insight_snapshot_id": "snapshot-1",
                "insight_summary": "Summary",
            },
        ),
        (
            "http://api/internal/tools/evaluate-campaign-plan",
            {
                "project_id": "project-1",
                "brief": {"property_segment": "apartments"},
                "insight_snapshot_id": "snapshot-1",
                "insight_summary": "Summary",
                "planning_constraints": {"budget_constraint": "50M VND"},
                "unavailable_signals": ["competitor budget benchmark"],
            },
        ),
        (
            "http://api/internal/tools/calculate-budget-forecast",
            {
                "project_id": "project-1",
                "campaign_plan_inputs": {
                    "lead_target": 120,
                    "campaign_duration_days": 21,
                },
            },
        ),
        (
            "http://api/internal/tools/recommend-campaign-timeline",
            {
                "project_id": "project-1",
                "campaign_plan_inputs": {
                    "objective": "lead_generation",
                    "segment": "apartments",
                },
            },
        ),
        (
            "http://api/internal/tools/collect-project-facts",
            {
                "project_id": "project-1",
                "brief": {"project_name": "Sunrise Riverside"},
                "user_material_refs": ["sales-kit.pdf"],
                "official_project_url": "https://example.com/project",
            },
        ),
        (
            "http://api/internal/tools/check-segment-constraints",
            {
                "project_id": "project-1",
                "property_segment": "apartments",
                "draft_context": {"format_type": "benefit_led"},
            },
        ),
        (
            "http://api/internal/tools/assess-claim-risk",
            {
                "project_id": "project-1",
                "draft_text": "Guaranteed rental yield",
                "project_facts": {"location": "Thu Duc"},
            },
        ),
        (
            "http://api/internal/tools/collect-insight-workflow",
            {
                "project_id": "project-1",
                "approved_source_ids": [],
                "user_context": "Metro demand context",
                "official_project_url": "https://example.com/project",
                "user_material_refs": ["sales-kit.pdf"],
            },
        ),
        (
            "http://api/internal/tools/create-project",
            {
                "project_name": "Sunrise Riverside",
                "property_segment": "apartments",
                "location": "Thu Duc, Ho Chi Minh City",
                "price_range": "3-5B VND",
                "key_selling_points": ["near metro", "river view"],
                "campaign_objective": "lead_generation",
                "buyer_profile": "young families",
                "tone": "professional_trustworthy",
                "promotion_details": "limited booking incentive",
            },
        ),
        (
            "http://api/internal/tools/prepare-campaign-context",
            {
                "project_id": "project-1",
                "insight_summary": "Verified local planning and buyer demand context.",
                "insight_snapshot_id": "snapshot-1",
                "planning_constraints": {"total_budget_vnd": 120000000},
                "unavailable_signals": ["competitor budget benchmark"],
            },
        ),
    ]


def test_internal_tool_http_errors_are_runtime_errors(monkeypatch) -> None:
    def fake_post(url: str, json: dict[str, object], timeout: float) -> _FakeResponse:
        return _FakeResponse({"error": {"code": "rule_service_failed"}}, status_code=503)

    monkeypatch.setattr(tools.httpx, "post", fake_post)

    with pytest.raises(RuntimeError, match="Internal tool call failed"):
        tools.evaluate_campaign_strategy(
            project_id="project-1",
            brief_json='{"property_segment":"apartments"}',
        )


def test_placeholder_project_id_is_rejected_before_http_call() -> None:
    with pytest.raises(RuntimeError, match="real project_id is required"):
        tools.collect_insight_workflow(project_id="placeholder_project_id")


def test_project_name_like_value_is_rejected_as_project_id() -> None:
    with pytest.raises(RuntimeError, match="system identifier returned by create_project or get_project"):
        require_real_project_id("EcoLake Garden")


def test_get_project_uses_get_request(monkeypatch) -> None:
    calls: list[tuple[str, float]] = []

    def fake_get(url: str, timeout: float) -> _FakeResponse:
        calls.append((url, timeout))
        return _FakeResponse({"data": {"project_id": "project-1"}})

    monkeypatch.setenv("CONTENT_CREATOR_INTERNAL_TOOLS_BASE_URL", "http://api/internal/tools")
    monkeypatch.setattr(tools.httpx, "get", fake_get)

    result = tools.get_project("project-1")

    assert result == {"data": {"project_id": "project-1"}}
    assert calls == [("http://api/internal/tools/get-project/project-1", 60.0)]


def test_update_project_posts_full_saved_brief(monkeypatch) -> None:
    calls: list[tuple[str, dict[str, object]]] = []

    def fake_post(url: str, json: dict[str, object], timeout: float) -> _FakeResponse:
        calls.append((url, json))
        return _FakeResponse({"data": {"project_id": "project-1"}})

    monkeypatch.setenv("CONTENT_CREATOR_INTERNAL_TOOLS_BASE_URL", "http://api/internal/tools")
    monkeypatch.setattr(tools.httpx, "post", fake_post)

    tools.update_project(
        project_id="project-1",
        project_name="Sunrise Riverside",
        property_segment="apartments",
        location="Thu Duc, Ho Chi Minh City",
        price_range="4-6B VND",
        key_selling_points=["near metro", "river view"],
        campaign_objective="lead_generation",
        buyer_profile="investors and young families",
        tone="professional_trustworthy",
    )

    assert calls == [
        (
            "http://api/internal/tools/update-project",
            {
                "project_id": "project-1",
                "project_name": "Sunrise Riverside",
                "property_segment": "apartments",
                "location": "Thu Duc, Ho Chi Minh City",
                "price_range": "4-6B VND",
                "key_selling_points": ["near metro", "river view"],
                "campaign_objective": "lead_generation",
                "buyer_profile": "investors and young families",
                "tone": "professional_trustworthy",
                "promotion_details": None,
            },
        )
    ]


def test_confirm_market_assumptions_posts_confirmation(monkeypatch) -> None:
    calls: list[tuple[str, dict[str, object]]] = []

    def fake_post(url: str, json: dict[str, object], timeout: float) -> _FakeResponse:
        calls.append((url, json))
        return _FakeResponse({"data": {"confirmed": True}})

    monkeypatch.setenv("CONTENT_CREATOR_INTERNAL_TOOLS_BASE_URL", "http://api/internal/tools")
    monkeypatch.setattr(tools.httpx, "post", fake_post)

    tools.confirm_market_assumptions(
        project_id="project-1",
        insight_snapshot_id="snapshot-1",
        assumptions_json='{"assumptions":[{"question":"Buyer demand","answer":"Confirmed by user."}]}',
    )

    assert calls == [
        (
            "http://api/internal/tools/confirm-market-assumptions",
            {
                "project_id": "project-1",
                "insight_snapshot_id": "snapshot-1",
                "assumptions": [
                    {"question": "Buyer demand", "answer": "Confirmed by user."}
                ],
                "confirmed": True,
            },
        )
    ]


def test_confirm_market_assumptions_schema_is_gemini_compatible() -> None:
    declaration = FunctionTool(tools.confirm_market_assumptions)._get_declaration()
    assumptions_schema = declaration.parameters.properties["assumptions_json"]

    assert assumptions_schema.type.value == "STRING"
    assert "assumptions" not in declaration.parameters.properties


def test_create_project_requires_enum_property_segment_and_filters_empty_selling_points(
    monkeypatch,
) -> None:
    calls: list[tuple[str, dict[str, object]]] = []

    def fake_post(url: str, json: dict[str, object], timeout: float) -> _FakeResponse:
        calls.append((url, json))
        return _FakeResponse({"data": {"project_id": "project-1"}})

    monkeypatch.setenv("CONTENT_CREATOR_INTERNAL_TOOLS_BASE_URL", "http://api/internal/tools")
    monkeypatch.setattr(tools.httpx, "post", fake_post)

    tools.create_project(
        project_name="Sunrise Riverside",
        property_segment="villas_luxury",
        location="Thu Duc, Ho Chi Minh City",
        price_range="3-5B VND",
        key_selling_points=["near metro", "", " river view "],
        campaign_objective="lead_generation",
        buyer_profile="young families",
        tone="professional_trustworthy",
        promotion_details=" limited booking incentive ",
    )

    assert calls == [
        (
            "http://api/internal/tools/create-project",
            {
                "project_name": "Sunrise Riverside",
                "property_segment": "villas_luxury",
                "location": "Thu Duc, Ho Chi Minh City",
                "price_range": "3-5B VND",
                "key_selling_points": ["near metro", "river view"],
                "campaign_objective": "lead_generation",
                "buyer_profile": "young families",
                "tone": "professional_trustworthy",
                "promotion_details": "limited booking incentive",
            },
        )
    ]


def test_property_segment_requires_backend_enum_value() -> None:
    assert require_property_segment("apartments") == "apartments"
    with pytest.raises(RuntimeError, match="property_segment must be one of"):
        require_property_segment("căn hộ ven sông")


def test_create_project_exposes_property_segment_enum_to_llm() -> None:
    declaration = FunctionTool(tools.create_project)._get_declaration()

    property_segment_schema = declaration.parameters.properties["property_segment"]

    assert property_segment_schema.enum == [
        "apartments",
        "land_plots",
        "townhouses",
        "villas_luxury",
        "commercial_real_estate",
    ]


def test_create_project_rejects_missing_required_fields_before_http_call() -> None:
    with pytest.raises(RuntimeError, match="project_name is required"):
        tools.create_project(
            project_name="",
            property_segment="apartments",
            location="Thu Duc",
            price_range="3-5B VND",
            key_selling_points=["near metro"],
            campaign_objective="lead_generation",
            buyer_profile="young families",
            tone="professional_trustworthy",
        )
