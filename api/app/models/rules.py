from typing import Any, Literal

from pydantic import BaseModel, Field


DecisionType = Literal[
    "campaign_strategy",
    "campaign_plan",
    "budget_forecast",
    "campaign_timeline",
    "segment_constraints",
    "claim_risk",
]


class Band(BaseModel):
    min: float
    max: float
    unit: str


class RiskFlag(BaseModel):
    category: str
    severity: str
    reason: str
    suggested_review_note: str


class CampaignStrategyRequest(BaseModel):
    project_id: str
    brief: dict[str, Any]
    insight_snapshot_id: str | None = None
    insight_summary: str | None = None


class CampaignStrategyDecision(BaseModel):
    rule_decision_id: str
    rule_version: str
    recommended_objective: str
    recommended_cta: str
    kpi_expectation_band: str
    approval_required: bool
    segment_constraints: list[str] = Field(default_factory=list)
    rationale_notes: list[str] = Field(default_factory=list)
    planning_assumptions: list[str] = Field(default_factory=list)
    evaluated_at: str


class CampaignPlanRequest(BaseModel):
    project_id: str
    brief: dict[str, Any]
    insight_snapshot_id: str | None = None
    insight_summary: str | None = None
    planning_constraints: dict[str, Any] = Field(default_factory=dict)
    unavailable_signals: list[str] = Field(default_factory=list)


class CampaignPlanDecision(BaseModel):
    campaign_plan_id: str
    rule_decision_id: str
    rule_version: str
    formula_version: str
    budget_band: Band
    daily_budget_band: Band
    kpi_forecast_band: dict[str, Band]
    recommended_duration_days: int
    content_cadence: dict[str, Any]
    confidence_level: str
    unavailable_inputs: list[str] = Field(default_factory=list)
    planning_assumptions: list[str] = Field(default_factory=list)
    estimate_disclaimer: str
    approval_required: bool
    evaluated_at: str


class CampaignPlanInputsRequest(BaseModel):
    project_id: str
    campaign_plan_inputs: dict[str, Any]


class SegmentConstraintsRequest(BaseModel):
    project_id: str
    property_segment: str
    draft_context: dict[str, Any] = Field(default_factory=dict)


class SegmentConstraintsDecision(BaseModel):
    rule_decision_id: str
    rule_version: str
    segment_constraints: list[str]
    evaluated_at: str


class ClaimRiskRequest(BaseModel):
    project_id: str
    draft_text: str
    project_facts: dict[str, Any] = Field(default_factory=dict)


class ClaimRiskDecision(BaseModel):
    rule_decision_id: str
    rule_version: str
    risk_flags: list[RiskFlag]
    approval_required: bool
    evaluated_at: str


class RuleDecisionRecord(BaseModel):
    rule_decision_id: str
    project_id: str
    decision_type: DecisionType
    rule_version: str
    input: dict[str, Any]
    output: dict[str, Any]
    timestamp: str
