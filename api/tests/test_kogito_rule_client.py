from typing import Any

from app.services.kogito_rule_client import KogitoRuleClient


class _FakeResponse:
    def __init__(self, body: dict[str, Any]) -> None:
        self._body = body

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._body


def test_kogito_client_calls_campaign_strategy_decision_service(monkeypatch) -> None:
    calls: list[dict[str, Any]] = []

    def fake_post(url, json, timeout):
        calls.append({"url": url, "json": json, "timeout": timeout})
        return _FakeResponse(
            {
                "rule_version": "campaign-strategy-v1",
                "recommended_objective": "lead_generation",
                "recommended_cta": "Register for consultation",
                "kpi_expectation_band": "lead_volume_medium",
                "approval_required": False,
                "segment_constraints": ["Use verified facts."],
                "rationale_notes": ["Objective follows campaign intent."],
                "planning_assumptions": ["Human review required."],
            }
        )

    monkeypatch.setattr("app.services.kogito_rule_client.httpx.post", fake_post)

    decision = KogitoRuleClient(
        base_url="http://rules.test",
        timeout_seconds=2,
    ).campaign_strategy(
        {
            "brief": {
                "property_segment": "apartments",
                "campaign_objective": "lead_generation",
                "buyer_profile": "young families",
            },
            "insight_summary": "Confirmed demand context.",
        }
    )

    assert calls[0]["url"] == (
        "http://rules.test/CampaignStrategy/EvaluateCampaignStrategy"
    )
    assert calls[0]["json"]["brief"]["property_segment"] == "apartments"
    assert decision["rule_version"] == "campaign-strategy-v1"
    assert decision["rule_decision_id"]
    assert decision["evaluated_at"]


def test_kogito_client_calls_campaign_plan_decision_service(monkeypatch) -> None:
    calls: list[dict[str, Any]] = []

    def fake_post(url, json, timeout):
        calls.append({"url": url, "json": json, "timeout": timeout})
        return _FakeResponse(
            {
                "rule_version": "campaign-planning-v1",
                "formula_version": "planning-formula-v1",
                "budget_band": {"min": 102000000, "max": 138000000, "unit": "VND"},
                "daily_budget_band": {
                    "min": 3400000,
                    "max": 4600000,
                    "unit": "VND",
                },
                "kpi_forecast_band": {
                    "leads": {"min": 192, "max": 288, "unit": "leads"},
                    "cpl": {"min": 425000, "max": 575000, "unit": "VND"},
                },
                "recommended_duration_days": 30,
                "content_cadence": {"posts_per_week": 4},
                "confidence_level": "medium",
                "unavailable_inputs": [],
                "planning_assumptions": ["Planning estimate only."],
                "estimate_disclaimer": "Planning estimate only.",
                "approval_required": False,
            }
        )

    monkeypatch.setattr("app.services.kogito_rule_client.httpx.post", fake_post)

    decision = KogitoRuleClient(
        base_url="http://rules.test/",
        timeout_seconds=3,
    ).campaign_plan(
        {
            "brief": {
                "property_segment": "apartments",
                "campaign_objective": "lead_generation",
            },
            "planning_constraints": {
                "total_budget_vnd": 120000000,
                "target_leads": 240,
                "campaign_days": 30,
            },
            "insight_summary": "Confirmed demand context.",
        }
    )

    assert calls[0]["url"] == "http://rules.test/CampaignPlan/EvaluateCampaignPlan"
    assert calls[0]["json"]["planning_constraints"]["total_budget_vnd"] == 120000000
    assert decision["rule_version"] == "campaign-planning-v1"
    assert decision["campaign_plan_id"]
    assert decision["rule_decision_id"]
    assert decision["evaluated_at"]
