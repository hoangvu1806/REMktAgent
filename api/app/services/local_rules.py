from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class LocalRules:
    strategy_rule_version = "campaign-strategy-v1"
    planning_rule_version = "campaign-planning-v1"
    formula_version = "planning-formula-v1"

    def evaluate(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if path == "campaign-strategy":
            return self._campaign_strategy(payload)
        if path in {"campaign-plan", "budget-forecast", "campaign-timeline"}:
            return self._campaign_plan(payload)
        if path == "segment-constraints":
            return self._segment_constraints_decision(payload)
        if path == "claim-risk":
            return self._claim_risk(payload)
        raise RuntimeError(f"Unsupported local rule path: {path}")

    def _campaign_strategy(self, payload: dict[str, Any]) -> dict[str, Any]:
        brief = _dict(payload.get("brief"))
        insight_context = _dict(payload.get("insight_context"))
        objective = str(brief.get("campaign_objective") or "lead_generation")
        unavailable_signal_count = int(
            insight_context.get("unavailable_signal_count") or 0
        )
        return {
            "rule_decision_id": _decision_id(),
            "rule_version": self.strategy_rule_version,
            "recommended_objective": objective,
            "recommended_cta": (
                "Book a consultation for offer details"
                if brief.get("promotion_details")
                else "Register for consultation"
            ),
            "kpi_expectation_band": _kpi_band(objective, unavailable_signal_count),
            "approval_required": unavailable_signal_count > 0,
            "segment_constraints": _segment_constraints(
                str(brief.get("property_segment") or "apartments"), ""
            ),
            "rationale_notes": [
                "Objective follows provided campaign intent when present.",
                "CTA prioritizes consultative lead capture for real estate campaigns.",
                "Buyer profile and insight availability influence planning confidence.",
            ],
            "planning_assumptions": [
                "Strategy recommendations are intended to guide downstream planning and copy generation.",
                "Missing insight signals may require human review before draft approval.",
            ],
            "evaluated_at": _utc_now(),
        }

    def _campaign_plan(self, payload: dict[str, Any]) -> dict[str, Any]:
        brief = _dict(payload.get("brief"))
        constraints = _dict(payload.get("planning_constraints"))
        insight_context = _dict(payload.get("insight_context"))
        segment = str(
            brief.get("property_segment")
            or constraints.get("property_segment")
            or "apartments"
        )
        budget = int(constraints.get("total_budget_vnd") or _default_budget(segment))
        days = int(constraints.get("campaign_days") or 30)
        leads = int(constraints.get("target_leads") or max(60, budget // 500_000))
        unavailable = list(
            insight_context.get("unavailable_inputs")
            or payload.get("unavailable_signals")
            or []
        )
        return {
            "campaign_plan_id": str(uuid4()),
            "rule_decision_id": _decision_id(),
            "rule_version": self.planning_rule_version,
            "formula_version": self.formula_version,
            "budget_band": _band(budget, "VND", 0.85, 1.15),
            "daily_budget_band": _band(max(1, budget / max(1, days)), "VND", 0.85, 1.15),
            "kpi_forecast_band": _kpi_forecast(budget, leads),
            "recommended_duration_days": days,
            "content_cadence": _content_cadence(
                segment, str(constraints.get("launch_phase") or "")
            ),
            "confidence_level": _confidence_level(unavailable, insight_context),
            "unavailable_inputs": unavailable,
            "planning_assumptions": [
                "Budget and KPI outputs are planning estimates.",
                "CPL ranges use conservative real estate lead-generation assumptions.",
                "Human review is required before treating plan outputs as final commitments.",
            ],
            "estimate_disclaimer": (
                "Planning estimate only; not financial, legal, investment, "
                "or guaranteed performance advice."
            ),
            "approval_required": bool(unavailable),
            "evaluated_at": _utc_now(),
        }

    def _segment_constraints_decision(self, payload: dict[str, Any]) -> dict[str, Any]:
        draft_context = _dict(payload.get("draft_context"))
        return {
            "rule_decision_id": _decision_id(),
            "rule_version": "segment-constraints-v1",
            "segment_constraints": _segment_constraints(
                str(payload.get("property_segment") or "apartments"),
                str(draft_context.get("format_type") or ""),
            ),
            "evaluated_at": _utc_now(),
        }

    def _claim_risk(self, payload: dict[str, Any]) -> dict[str, Any]:
        draft = str(payload.get("draft_text") or "").lower()
        project_facts = _dict(payload.get("project_facts"))
        flags = [
            flag
            for flag in [
                _risk_if(
                    "discount" in draft or "% off" in draft or "ưu đãi" in draft,
                    "discount",
                    "medium",
                    "Discount or promotion claim needs offer verification.",
                    "Verify promotion terms before approval.",
                ),
                _risk_if(
                    "ownership" in draft or "instant ownership" in draft or "sổ" in draft,
                    "ownership",
                    "high",
                    "Ownership/legal status claim needs factual support.",
                    "Confirm legal and ownership documents before approval.",
                ),
                _risk_if(
                    "handover" in draft
                    or "bàn giao" in draft
                    or project_facts.get("handover_status") == "planned",
                    "handover_timing",
                    "medium",
                    "Handover timing claim needs project schedule support.",
                    "Check official handover timeline.",
                ),
                _risk_if(
                    "financing" in draft or "loan" in draft or "vay" in draft,
                    "financing",
                    "medium",
                    "Financing claim needs lender/program verification.",
                    "Verify financing terms.",
                ),
                _risk_if(
                    "rental yield" in draft or "yield" in draft or "cho thuê" in draft,
                    "rental_yield",
                    "high",
                    "Rental yield claim can imply investment performance.",
                    "Remove guarantee language or add verified basis.",
                ),
                _risk_if(
                    "guaranteed" in draft or "cam kết" in draft or "profit" in draft,
                    "investment_potential",
                    "high",
                    "Guaranteed return or profit claim is risk-sensitive.",
                    "Avoid guaranteed investment performance claims.",
                ),
            ]
            if flag is not None
        ]
        return {
            "rule_decision_id": _decision_id(),
            "rule_version": "claim-risk-v1",
            "risk_flags": flags,
            "approval_required": bool(flags),
            "evaluated_at": _utc_now(),
        }


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _decision_id() -> str:
    return f"rd_{uuid4()}"


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _band(center: float, unit: str, low: float, high: float) -> dict[str, Any]:
    return {"min": round(center * low, 2), "max": round(center * high, 2), "unit": unit}


def _risk_if(
    condition: bool, category: str, severity: str, reason: str, note: str
) -> dict[str, str] | None:
    if not condition:
        return None
    return {
        "category": category,
        "severity": severity,
        "reason": reason,
        "suggested_review_note": note,
    }


def _default_budget(segment: str) -> int:
    return {
        "commercial_real_estate": 180_000_000,
        "villas_luxury": 160_000_000,
        "land_plots": 90_000_000,
    }.get(segment, 120_000_000)


def _segment_constraints(segment: str, format_type: str) -> list[str]:
    constraints = [
        "Avoid guaranteed investment-return claims.",
        "Use verified project facts for legal, price, handover, and financing claims.",
    ]
    if segment == "land_plots":
        constraints.append("Highlight planning/legal clarity only when source-backed.")
    elif segment == "commercial_real_estate":
        constraints.append("Avoid implying guaranteed tenant demand or rental yield.")
    elif segment == "villas_luxury":
        constraints.append("Keep luxury positioning specific and evidence-backed.")
    if format_type == "promotion_offer":
        constraints.append("Verify promotion terms, dates, and eligibility before publishing.")
    return constraints


def _kpi_band(objective: str, unavailable_signal_count: int) -> str:
    if objective == "awareness":
        return "reach_engagement_medium"
    if unavailable_signal_count:
        return "lead_volume_cautious"
    return "lead_volume_medium"


def _kpi_forecast(budget: int, leads: int) -> dict[str, dict[str, Any]]:
    return {
        "leads": _band(leads, "leads", 0.8, 1.2),
        "cpl": _band(max(1, budget / max(1, leads)), "VND", 0.85, 1.15),
        "clicks": _band(leads * 12, "clicks", 0.8, 1.2),
        "reach": _band(leads * 180, "people", 0.8, 1.2),
    }


def _content_cadence(segment: str, launch_phase: str) -> dict[str, Any]:
    return {
        "posts_per_week": 3
        if segment == "commercial_real_estate"
        else (5 if launch_phase == "launch" else 4),
        "creative_variants_per_week": 3,
        "review_checkpoint_days": [7, 14, 21],
    }


def _confidence_level(unavailable: list[Any], insight_context: dict[str, Any]) -> str:
    if unavailable:
        return "low"
    if int(insight_context.get("source_backed_signal_count") or 0) >= 3:
        return "medium"
    return "cautious"
