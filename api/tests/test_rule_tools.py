from fastapi.testclient import TestClient

from app.main import app


def _project_payload() -> dict[str, object]:
    return {
        "project_name": "Sunrise Riverside",
        "property_segment": "apartments",
        "location": "Thu Duc, Ho Chi Minh City",
        "price_range": "3-5B VND",
        "key_selling_points": ["near metro", "river view", "ready handover"],
        "campaign_objective": "lead_generation",
        "buyer_profile": "young families and first-time buyers",
        "tone": "professional_trustworthy",
        "promotion_details": "limited booking incentive",
    }


def _create_project(client: TestClient) -> tuple[str, dict[str, object]]:
    response = client.post("/projects", json=_project_payload())
    assert response.status_code == 201
    project = response.json()["data"]
    return project["project_id"], project["brief"]


def test_evaluate_campaign_strategy_returns_rule_backed_decision(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv(
        "SQLITE_DATABASE_PATH", str(tmp_path / "content_creator.sqlite3")
    )
    client = TestClient(app)
    project_id, brief = _create_project(client)

    response = client.post(
        "/internal/tools/evaluate-campaign-strategy",
        json={
            "project_id": project_id,
            "brief": brief,
            "insight_snapshot_id": "insight-1",
            "insight_summary": "Transit-oriented young family demand.",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["rule_decision_id"]
    assert data["rule_version"] == "campaign-strategy-v1"
    assert data["recommended_objective"] == "lead_generation"
    assert data["recommended_cta"]
    assert data["kpi_expectation_band"]
    assert data["approval_required"] is False
    assert data["segment_constraints"]
    assert data["rationale_notes"]
    assert data["planning_assumptions"]

    diagnostics = client.get(f"/internal/tools/rule-decisions/{project_id}")
    assert diagnostics.status_code == 200
    records = diagnostics.json()["data"]
    assert len(records) == 1
    assert records[0]["decision_type"] == "campaign_strategy"
    assert records[0]["output"]["rule_decision_id"] == data["rule_decision_id"]


def test_campaign_planning_tools_return_budget_kpi_and_timing_estimates(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv(
        "SQLITE_DATABASE_PATH", str(tmp_path / "content_creator.sqlite3")
    )
    client = TestClient(app)
    project_id, brief = _create_project(client)

    plan_response = client.post(
        "/internal/tools/evaluate-campaign-plan",
        json={
            "project_id": project_id,
            "brief": brief,
            "insight_snapshot_id": "insight-1",
            "insight_summary": "Demand is strongest for metro-adjacent apartments.",
            "planning_constraints": {
                "total_budget_vnd": 120000000,
                "target_leads": 240,
                "campaign_days": 30,
            },
            "unavailable_signals": [],
        },
    )

    assert plan_response.status_code == 200
    plan = plan_response.json()["data"]
    assert plan["campaign_plan_id"]
    assert plan["rule_version"] == "campaign-planning-v1"
    assert plan["formula_version"] == "planning-formula-v1"
    assert plan["budget_band"]["unit"] == "VND"
    assert plan["daily_budget_band"]["unit"] == "VND"
    assert plan["kpi_forecast_band"]["leads"]["unit"] == "leads"
    assert plan["recommended_duration_days"] == 30
    assert plan["content_cadence"]["posts_per_week"] >= 3
    assert plan["estimate_disclaimer"]
    assert plan["approval_required"] is False
    assert plan["planning_assumptions"]

    budget_response = client.post(
        "/internal/tools/calculate-budget-forecast",
        json={
            "project_id": project_id,
            "campaign_plan_inputs": {
                "property_segment": "apartments",
                "total_budget_vnd": 90000000,
                "target_leads": 180,
                "campaign_days": 30,
            },
        },
    )
    assert budget_response.status_code == 200
    assert budget_response.json()["data"]["budget_band"]["unit"] == "VND"

    timeline_response = client.post(
        "/internal/tools/recommend-campaign-timeline",
        json={
            "project_id": project_id,
            "campaign_plan_inputs": {
                "property_segment": "apartments",
                "campaign_days": 21,
                "launch_phase": "booking",
            },
        },
    )
    assert timeline_response.status_code == 200
    assert timeline_response.json()["data"]["recommended_duration_days"] == 21


def test_claim_risk_and_segment_constraints_flag_sensitive_real_estate_claims(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv(
        "SQLITE_DATABASE_PATH", str(tmp_path / "content_creator.sqlite3")
    )
    client = TestClient(app)
    project_id, _brief = _create_project(client)

    segment_response = client.post(
        "/internal/tools/check-segment-constraints",
        json={
            "project_id": project_id,
            "property_segment": "apartments",
            "draft_context": {"format_type": "promotion_offer"},
        },
    )
    assert segment_response.status_code == 200
    assert segment_response.json()["data"]["segment_constraints"]
    assert "Verify promotion terms, dates, and eligibility before publishing." in (
        segment_response.json()["data"]["segment_constraints"]
    )

    risk_response = client.post(
        "/internal/tools/assess-claim-risk",
        json={
            "project_id": project_id,
            "draft_text": "Guaranteed 18% rental yield, instant ownership, 30% discount.",
            "project_facts": {"handover_status": "planned"},
        },
    )
    assert risk_response.status_code == 200
    data = risk_response.json()["data"]
    categories = {flag["category"] for flag in data["risk_flags"]}
    assert {
        "discount",
        "ownership",
        "rental_yield",
        "investment_potential",
    } <= categories
    assert data["approval_required"] is True
