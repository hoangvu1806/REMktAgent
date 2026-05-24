from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import httpx

from app.services.local_rules import LocalRules


class KogitoRuleClient:
    def __init__(self, base_url: str | None = None, timeout_seconds: float = 30) -> None:
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds

    def campaign_strategy(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post_or_local("campaign-strategy", payload)

    def campaign_plan(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post_or_local("campaign-plan", payload)

    def budget_forecast(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post_or_local("budget-forecast", payload)

    def campaign_timeline(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post_or_local("campaign-timeline", payload)

    def segment_constraints(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post_or_local("segment-constraints", payload)

    def claim_risk(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post_or_local("claim-risk", payload)

    def _post_or_local(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.base_url:
            endpoint, dmn_payload, decision_name = self._dmn_request(path, payload)
            response = httpx.post(
                f"{self.base_url.rstrip('/')}/{endpoint}",
                json=dmn_payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            body = response.json()
            if not isinstance(body, dict):
                raise RuntimeError("Kogito rule service returned non-object JSON")
            return self._dmn_response(path, body, decision_name)
        return LocalRules().evaluate(path, payload)

    def _dmn_request(
        self, path: str, payload: dict[str, Any]
    ) -> tuple[str, dict[str, Any], str]:
        if path == "campaign-strategy":
            brief = _dict(payload.get("brief"))
            insight_summary = str(payload.get("insight_summary") or "")
            unavailable_signals = list(payload.get("unavailable_signals") or [])
            return (
                "CampaignStrategy/EvaluateCampaignStrategy",
                {
                    "brief": {
                        "property_segment": brief.get("property_segment") or "apartments",
                        "campaign_objective": brief.get("campaign_objective")
                        or "lead_generation",
                        "buyer_profile": brief.get("buyer_profile") or "",
                        "promotion_details": brief.get("promotion_details") or "",
                    },
                    "insight_context": {
                        "summary": insight_summary,
                        "source_backed_signal_count": 3,
                        "unavailable_signal_count": len(unavailable_signals),
                    },
                },
                "EvaluateCampaignStrategy",
            )
        if path in {"campaign-plan", "budget-forecast", "campaign-timeline"}:
            brief = _dict(payload.get("brief"))
            constraints = _dict(payload.get("planning_constraints"))
            segment = brief.get("property_segment") or constraints.get("property_segment")
            unavailable_signals = list(payload.get("unavailable_signals") or [])
            service_name = {
                "campaign-plan": "EvaluateCampaignPlan",
                "budget-forecast": "CalculateBudgetForecast",
                "campaign-timeline": "RecommendCampaignTimeline",
            }[path]
            return (
                f"CampaignPlan/{service_name}",
                {
                    "brief": {
                        "property_segment": segment or "apartments",
                        "campaign_objective": brief.get("campaign_objective")
                        or constraints.get("campaign_objective")
                        or "lead_generation",
                    },
                    "planning_constraints": {
                        "total_budget_vnd": constraints.get("total_budget_vnd")
                        or 120_000_000,
                        "target_leads": constraints.get("target_leads") or 240,
                        "campaign_days": constraints.get("campaign_days") or 30,
                        "launch_phase": constraints.get("launch_phase") or "",
                    },
                    "insight_context": {
                        "summary": str(payload.get("insight_summary") or ""),
                        "source_backed_signal_count": 3,
                        "unavailable_inputs": unavailable_signals,
                    },
                },
                service_name,
            )
        if path == "segment-constraints":
            return (
                "SegmentConstraints/CheckSegmentConstraints",
                {
                    "property_segment": payload.get("property_segment") or "apartments",
                    "draft_context": _dict(payload.get("draft_context")),
                },
                "CheckSegmentConstraints",
            )
        if path == "claim-risk":
            return (
                "ClaimRisk/AssessClaimRisk",
                {
                    "draft_text": str(payload.get("draft_text") or "").lower(),
                    "project_facts": _dict(payload.get("project_facts")),
                },
                "AssessClaimRisk",
            )
        raise RuntimeError(f"Unsupported Kogito rule path: {path}")

    def _dmn_response(
        self, path: str, body: dict[str, Any], decision_name: str
    ) -> dict[str, Any]:
        if "rule_version" in body:
            decision = dict(body)
        else:
            decision = body.get(decision_name)
            if not isinstance(decision, dict):
                raise RuntimeError(f"Kogito DMN response missing {decision_name}")
            decision = dict(decision)
        decision.setdefault("rule_decision_id", _decision_id())
        decision.setdefault("evaluated_at", _utc_now())
        if path in {"campaign-plan", "budget-forecast", "campaign-timeline"}:
            decision.setdefault("campaign_plan_id", str(uuid4()))
        return decision


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _decision_id() -> str:
    return f"rd_{uuid4()}"


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

