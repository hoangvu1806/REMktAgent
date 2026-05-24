import os
from datetime import UTC, datetime
from typing import Any, Callable

from app.models.rules import (
    CampaignPlanDecision,
    CampaignPlanInputsRequest,
    CampaignPlanRequest,
    CampaignStrategyDecision,
    CampaignStrategyRequest,
    ClaimRiskDecision,
    ClaimRiskRequest,
    DecisionType,
    RuleDecisionRecord,
    SegmentConstraintsDecision,
    SegmentConstraintsRequest,
)
from app.services.kogito_rule_client import KogitoRuleClient
from app.storage.rule_decision_store import RuleDecisionStore


class RuleService:
    def __init__(
        self,
        client: KogitoRuleClient | None = None,
        store: RuleDecisionStore | None = None,
    ) -> None:
        self.client = client or KogitoRuleClient(
            base_url=os.environ.get("KOGITO_RULE_SERVICE_URL"),
            timeout_seconds=float(os.environ.get("KOGITO_RULE_TIMEOUT_SECONDS", "30")),
        )
        self.store = store or RuleDecisionStore()

    def evaluate_campaign_strategy(
        self, payload: CampaignStrategyRequest
    ) -> CampaignStrategyDecision:
        return self._evaluate(
            payload=payload,
            decision_type="campaign_strategy",
            client_call=self.client.campaign_strategy,
            decision_model=CampaignStrategyDecision,
        )

    def evaluate_campaign_plan(self, payload: CampaignPlanRequest) -> CampaignPlanDecision:
        return self._evaluate_plan(
            decision_type="campaign_plan",
            project_id=payload.project_id,
            input_payload=payload.model_dump(),
            rule_payload=payload.model_dump(),
            client_call=self.client.campaign_plan,
        )

    def calculate_budget_forecast(
        self, payload: CampaignPlanInputsRequest
    ) -> CampaignPlanDecision:
        return self._evaluate_plan(
            decision_type="budget_forecast",
            project_id=payload.project_id,
            input_payload=payload.model_dump(),
            rule_payload=_campaign_plan_inputs_payload(payload),
            client_call=self.client.budget_forecast,
        )

    def recommend_campaign_timeline(
        self, payload: CampaignPlanInputsRequest
    ) -> CampaignPlanDecision:
        return self._evaluate_plan(
            decision_type="campaign_timeline",
            project_id=payload.project_id,
            input_payload=payload.model_dump(),
            rule_payload=_campaign_plan_inputs_payload(payload),
            client_call=self.client.campaign_timeline,
        )

    def check_segment_constraints(
        self, payload: SegmentConstraintsRequest
    ) -> SegmentConstraintsDecision:
        return self._evaluate(
            payload=payload,
            decision_type="segment_constraints",
            client_call=self.client.segment_constraints,
            decision_model=SegmentConstraintsDecision,
        )

    def assess_claim_risk(self, payload: ClaimRiskRequest) -> ClaimRiskDecision:
        return self._evaluate(
            payload=payload,
            decision_type="claim_risk",
            client_call=self.client.claim_risk,
            decision_model=ClaimRiskDecision,
        )

    def list_rule_decisions(self, project_id: str) -> list[RuleDecisionRecord]:
        return self.store.list_by_project(project_id)

    def _evaluate(
        self,
        *,
        payload: Any,
        decision_type: DecisionType,
        client_call: Callable[[dict[str, Any]], dict[str, Any]],
        decision_model: Any,
    ) -> Any:
        input_payload = payload.model_dump()
        data = decision_model.model_validate(client_call(input_payload))
        self._store_decision(
            project_id=payload.project_id,
            decision_type=decision_type,
            input_payload=input_payload,
            data=data,
        )
        return data

    def _evaluate_plan(
        self,
        *,
        decision_type: DecisionType,
        project_id: str,
        input_payload: dict[str, Any],
        rule_payload: dict[str, Any],
        client_call: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> CampaignPlanDecision:
        data = CampaignPlanDecision.model_validate(client_call(rule_payload))
        self._store_decision(
            project_id=project_id,
            decision_type=decision_type,
            input_payload=input_payload,
            data=data,
        )
        return data

    def _store_decision(
        self,
        *,
        project_id: str,
        decision_type: DecisionType,
        input_payload: dict[str, Any],
        data: Any,
    ) -> None:
        self.store.save(
            RuleDecisionRecord(
                rule_decision_id=data.rule_decision_id,
                project_id=project_id,
                decision_type=decision_type,
                rule_version=data.rule_version,
                input=input_payload,
                output=data.model_dump(),
                timestamp=data.evaluated_at or _utc_now(),
            )
        )


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _campaign_plan_inputs_payload(
    payload: CampaignPlanInputsRequest,
) -> dict[str, Any]:
    inputs = payload.campaign_plan_inputs
    return {
        "project_id": payload.project_id,
        "brief": {"property_segment": inputs.get("property_segment")},
        "planning_constraints": inputs,
        "unavailable_signals": inputs.get("unavailable_signals", []),
    }
