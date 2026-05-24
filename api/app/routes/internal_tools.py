from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.responses import ApiResponse
from app.models.project import Project, ProjectBriefCreate
from app.models.rules import (
    CampaignPlanDecision,
    CampaignPlanInputsRequest,
    CampaignPlanRequest,
    CampaignStrategyDecision,
    CampaignStrategyRequest,
    ClaimRiskDecision,
    ClaimRiskRequest,
    RuleDecisionRecord,
    SegmentConstraintsDecision,
    SegmentConstraintsRequest,
)
from app.routes.internal_tool_models import (
    CollectInsightWorkflowRequest,
    CollectProjectFactsRequest,
    ConfirmMarketAssumptionsRequest,
    CreateProjectToolRequest,
    PrepareCampaignContextRequest,
    UpdateProjectToolRequest,
)
from app.routes.response_helpers import correlation_id, not_found
from app.services.agent_workflow_service import (
    AgentWorkflowService,
    CampaignContextBundle,
    InsightWorkflowBundle,
)
from app.services.insight_service import InsightService
from app.services.insight_service import InsightNotFoundError
from app.services.project_service import ProjectNotFoundError
from app.services.project_service import ProjectService
from app.services.rule_service import RuleService


router = APIRouter(prefix="/internal/tools", tags=["internal-tools"])


@router.post("/collect-project-facts", response_model=ApiResponse[dict[str, Any]])
def collect_project_facts(
    payload: CollectProjectFactsRequest,
) -> ApiResponse[dict[str, Any]]:
    data = InsightService().collect_project_facts(
        project_id=payload.project_id,
        brief=payload.brief,
        user_material_refs=payload.user_material_refs,
        official_project_url=payload.official_project_url,
        resolve_external_content=False,
    )
    return ApiResponse(data=data, meta={"correlation_id": correlation_id()})


@router.post("/create-project", response_model=ApiResponse[Project])
def create_project(payload: CreateProjectToolRequest) -> ApiResponse[Project]:
    data = ProjectService().create_project(
        ProjectBriefCreate.model_validate(payload.model_dump())
    )
    return ApiResponse(data=data, meta={"correlation_id": correlation_id()})


@router.post("/update-project", response_model=ApiResponse[Project])
def update_project(
    payload: UpdateProjectToolRequest,
) -> ApiResponse[Project] | JSONResponse:
    try:
        data = ProjectService().update_project(
            payload.project_id,
            ProjectBriefCreate.model_validate(
                payload.model_dump(exclude={"project_id"})
            ),
        )
    except ProjectNotFoundError:
        return not_found("Project was not found.", {"project_id": payload.project_id})
    return ApiResponse(data=data, meta={"correlation_id": correlation_id()})


@router.get("/get-project/{project_id}", response_model=ApiResponse[Project])
def get_project(project_id: str) -> ApiResponse[Project] | JSONResponse:
    try:
        data = ProjectService().get_project(project_id)
    except ProjectNotFoundError:
        return not_found("Project was not found.", {"project_id": project_id})
    return ApiResponse(data=data, meta={"correlation_id": correlation_id()})


@router.post(
    "/collect-insight-workflow",
    response_model=ApiResponse[InsightWorkflowBundle],
)
def collect_insight_workflow(
    payload: CollectInsightWorkflowRequest,
) -> ApiResponse[InsightWorkflowBundle] | JSONResponse:
    try:
        data = AgentWorkflowService().collect_insight_workflow(
            payload.project_id,
            approved_source_ids=payload.approved_source_ids,
            user_context=payload.user_context,
            official_project_url=payload.official_project_url,
            user_material_refs=payload.user_material_refs,
        )
    except ProjectNotFoundError:
        return not_found("Project was not found.", {"project_id": payload.project_id})
    return ApiResponse(data=data, meta={"correlation_id": correlation_id()})


@router.post(
    "/confirm-market-assumptions",
    response_model=ApiResponse[dict[str, Any]],
)
def confirm_market_assumptions(
    payload: ConfirmMarketAssumptionsRequest,
) -> ApiResponse[dict[str, Any]] | JSONResponse:
    try:
        snapshot = InsightService().update_assumptions(
            payload.project_id,
            payload.insight_snapshot_id,
            payload,
        )
    except ProjectNotFoundError:
        return not_found("Project was not found.", {"project_id": payload.project_id})
    except InsightNotFoundError:
        return not_found(
            "Insight snapshot was not found.",
            {"snapshot_id": payload.insight_snapshot_id},
        )
    return ApiResponse(
        data={
            "project_id": snapshot.project_id,
            "insight_snapshot_id": snapshot.snapshot_id,
            "confirmed": snapshot.confirmed,
            "assumptions": [item.model_dump() for item in snapshot.assumptions],
            "summary": snapshot.summary,
            "unavailable_signals": snapshot.unavailable_signals,
        },
        meta={"correlation_id": correlation_id()},
    )


@router.post(
    "/prepare-campaign-context",
    response_model=ApiResponse[CampaignContextBundle],
)
def prepare_campaign_context(
    payload: PrepareCampaignContextRequest,
) -> ApiResponse[CampaignContextBundle] | JSONResponse:
    try:
        data = AgentWorkflowService().prepare_campaign_context(
            payload.project_id,
            insight_summary=payload.insight_summary,
            insight_snapshot_id=payload.insight_snapshot_id,
            planning_constraints=payload.planning_constraints,
            unavailable_signals=payload.unavailable_signals,
        )
    except ProjectNotFoundError:
        return not_found("Project was not found.", {"project_id": payload.project_id})
    return ApiResponse(data=data, meta={"correlation_id": correlation_id()})


@router.post(
    "/evaluate-campaign-strategy",
    response_model=ApiResponse[CampaignStrategyDecision],
)
def evaluate_campaign_strategy(
    payload: CampaignStrategyRequest,
) -> ApiResponse[CampaignStrategyDecision]:
    data = RuleService().evaluate_campaign_strategy(payload)
    return ApiResponse(data=data, meta={"correlation_id": correlation_id()})


@router.post(
    "/evaluate-campaign-plan",
    response_model=ApiResponse[CampaignPlanDecision],
)
def evaluate_campaign_plan(
    payload: CampaignPlanRequest,
) -> ApiResponse[CampaignPlanDecision]:
    data = RuleService().evaluate_campaign_plan(payload)
    return ApiResponse(data=data, meta={"correlation_id": correlation_id()})


@router.post(
    "/calculate-budget-forecast",
    response_model=ApiResponse[CampaignPlanDecision],
)
def calculate_budget_forecast(
    payload: CampaignPlanInputsRequest,
) -> ApiResponse[CampaignPlanDecision]:
    data = RuleService().calculate_budget_forecast(payload)
    return ApiResponse(data=data, meta={"correlation_id": correlation_id()})


@router.post(
    "/recommend-campaign-timeline",
    response_model=ApiResponse[CampaignPlanDecision],
)
def recommend_campaign_timeline(
    payload: CampaignPlanInputsRequest,
) -> ApiResponse[CampaignPlanDecision]:
    data = RuleService().recommend_campaign_timeline(payload)
    return ApiResponse(data=data, meta={"correlation_id": correlation_id()})


@router.post(
    "/check-segment-constraints",
    response_model=ApiResponse[SegmentConstraintsDecision],
)
def check_segment_constraints(
    payload: SegmentConstraintsRequest,
) -> ApiResponse[SegmentConstraintsDecision]:
    data = RuleService().check_segment_constraints(payload)
    return ApiResponse(data=data, meta={"correlation_id": correlation_id()})


@router.post(
    "/assess-claim-risk",
    response_model=ApiResponse[ClaimRiskDecision],
)
def assess_claim_risk(payload: ClaimRiskRequest) -> ApiResponse[ClaimRiskDecision]:
    data = RuleService().assess_claim_risk(payload)
    return ApiResponse(data=data, meta={"correlation_id": correlation_id()})


@router.get(
    "/rule-decisions/{project_id}",
    response_model=ApiResponse[list[RuleDecisionRecord]],
)
def list_rule_decisions(project_id: str) -> ApiResponse[list[RuleDecisionRecord]]:
    data = RuleService().list_rule_decisions(project_id)
    return ApiResponse(data=data, meta={"correlation_id": correlation_id()})
