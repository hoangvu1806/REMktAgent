from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.models.insight import InsightCollectionRequest
from app.models.project import Project
from app.models.rules import (
    CampaignPlanDecision,
    CampaignPlanRequest,
    CampaignStrategyDecision,
    CampaignStrategyRequest,
)
from app.services.insight_service import InsightService
from app.services.project_service import ProjectService
from app.services.rule_service import RuleService


class InsightWorkflowBundle(BaseModel):
    project_id: str
    project_name: str
    insight_snapshot_id: str | None = None
    insight_status: str = "partial"
    ready_for_confirmation: bool = False
    questions: list[str] = Field(default_factory=list)
    approved_source_ids: list[str] = Field(default_factory=list)
    required_search_agents: list[str] = Field(default_factory=list)
    specialist_tasks: list[dict[str, str]] = Field(default_factory=list)
    summary_sections: dict[str, list[str]] = Field(default_factory=dict)
    project_facts: dict[str, Any]
    local_context: dict[str, Any]
    market_signals: dict[str, Any]
    competitor_positioning: dict[str, Any]
    insight_summary: str
    unavailable_signals: list[str] = Field(default_factory=list)


class CampaignContextBundle(BaseModel):
    project_id: str
    project_name: str
    insight_snapshot_id: str | None = None
    insight_summary: str
    strategy: CampaignStrategyDecision
    campaign_plan: CampaignPlanDecision


class AgentWorkflowService:
    def __init__(
        self,
        *,
        project_service: ProjectService | None = None,
        insight_service: InsightService | None = None,
        rule_service: RuleService | None = None,
    ) -> None:
        self.project_service = project_service or ProjectService()
        self.insight_service = insight_service or InsightService()
        self.rule_service = rule_service or RuleService()

    def collect_insight_workflow(
        self,
        project_id: str,
        *,
        approved_source_ids: list[str] | None = None,
        user_context: str | None = None,
        official_project_url: str | None = None,
        user_material_refs: list[str] | None = None,
    ) -> InsightWorkflowBundle:
        project = self.project_service.get_project(project_id)
        questions = self._market_research_questions(project)
        snapshot = self.insight_service.collect_snapshot(
            project.project_id,
            InsightCollectionRequest(
                approved_source_ids=[],
                user_context=user_context,
            ),
        )

        project_facts = self.insight_service.collect_project_facts(
            project_id=project.project_id,
            brief=self._brief_payload(project),
            user_material_refs=user_material_refs or [],
            official_project_url=official_project_url,
            resolve_external_content=False,
        )
        local_context = self.insight_service.collect_local_context(
            project_id=project.project_id,
            location=project.brief.location,
            property_segment=project.brief.property_segment.value,
            approved_source_ids=[],
            resolve_external_content=False,
        )
        market_signals = self.insight_service.collect_market_signals(
            project_id=project.project_id,
            questions=questions,
            user_context=user_context,
            resolve_external_content=False,
        )
        competitor_positioning = self.insight_service.collect_competitor_positioning(
            project_id=project.project_id,
            location=project.brief.location,
            property_segment=project.brief.property_segment.value,
            price_range=project.brief.price_range,
            approved_source_ids=[],
            resolve_external_content=False,
        )
        required_search_agents = [
            "local_context_agent",
            "market_research_agent",
            "competitor_positioning_agent",
        ]
        unavailable_signals = [
            "local context search not completed",
            "market signal search not completed",
            "competitor positioning search not completed",
        ]

        return InsightWorkflowBundle(
            project_id=project.project_id,
            project_name=project.project_name,
            insight_snapshot_id=snapshot.snapshot_id,
            insight_status="partial",
            ready_for_confirmation=False,
            questions=questions,
            approved_source_ids=[],
            required_search_agents=required_search_agents,
            specialist_tasks=self._specialist_tasks(project),
            summary_sections=self._summary_sections(
                project,
                user_context=user_context,
                unavailable_signals=unavailable_signals,
            ),
            project_facts=project_facts,
            local_context=local_context,
            market_signals=market_signals,
            competitor_positioning=competitor_positioning,
            insight_summary=self._insight_summary(project, questions, unavailable_signals),
            unavailable_signals=unavailable_signals,
        )

    def prepare_campaign_context(
        self,
        project_id: str,
        *,
        insight_summary: str,
        insight_snapshot_id: str | None = None,
        planning_constraints: dict[str, Any] | None = None,
        unavailable_signals: list[str] | None = None,
    ) -> CampaignContextBundle:
        project = self.project_service.get_project(project_id)
        strategy = self.rule_service.evaluate_campaign_strategy(
            CampaignStrategyRequest(
                project_id=project.project_id,
                brief=self._brief_payload(project),
                insight_snapshot_id=insight_snapshot_id,
                insight_summary=insight_summary,
            )
        )
        campaign_plan = self.rule_service.evaluate_campaign_plan(
            CampaignPlanRequest(
                project_id=project.project_id,
                brief=self._brief_payload(project),
                insight_snapshot_id=insight_snapshot_id,
                insight_summary=insight_summary,
                planning_constraints=planning_constraints or {},
                unavailable_signals=unavailable_signals or [],
            )
        )
        return CampaignContextBundle(
            project_id=project.project_id,
            project_name=project.project_name,
            insight_snapshot_id=insight_snapshot_id,
            insight_summary=insight_summary,
            strategy=strategy,
            campaign_plan=campaign_plan,
        )

    def _market_research_questions(self, project: Project) -> list[str]:
        brief = project.brief
        segment = brief.property_segment.value.replace("_", " ")
        selling_points = ", ".join(brief.key_selling_points[:3])
        return [
            f"Bối cảnh quy hoạch, hạ tầng, giao thông và tiện ích nào quan trọng tại {brief.location}?",
            f"Tín hiệu nhu cầu nào phù hợp với phân khúc {segment} tại {brief.location}?",
            f"Đối thủ hoặc dự án cùng khu vực đang định vị ra sao trong khoảng giá {brief.price_range}?",
            f"Góc nội dung nào hỗ trợ tốt nhất mục tiêu {brief.campaign_objective} cho nhóm {brief.buyer_profile}?",
            f"Luận điểm nào cần xác minh trước khi dùng các selling point: {selling_points}?",
        ]

    def _insight_summary(
        self, project: Project, questions: list[str], unavailable_signals: list[str]
    ) -> str:
        return (
            f"Đã tạo insight snapshot cho {project.project_name} tại "
            f"{project.brief.location}: "
            f"{len(questions)} câu hỏi nghiên cứu, {len(unavailable_signals)} nguồn chưa khả dụng."
        )

    def _specialist_tasks(
        self, project: Project
    ) -> list[dict[str, str]]:
        brief = project.brief
        return [
            {
                "agent": "project_fact_agent",
                "task": "Chuẩn hóa brief, tài liệu người dùng và nguồn chính thức nếu có.",
            },
            {
                "agent": "approved_source_search_agent",
                "task": "Tìm kiếm web linh hoạt, trích nguồn/link đáng tin cậy và tóm tắt bằng chứng liên quan.",
            },
            {
                "agent": "local_context_agent",
                "task": f"Thu thập bối cảnh quy hoạch, hạ tầng, giao thông và tiện ích tại {brief.location}.",
            },
            {
                "agent": "market_research_agent",
                "task": f"Tổng hợp tín hiệu nhu cầu cho {brief.property_segment.value} và nhóm {brief.buyer_profile}.",
            },
            {
                "agent": "competitor_positioning_agent",
                "task": f"So sánh định vị dự án cùng khu vực/phân khúc trong khoảng {brief.price_range}.",
            },
        ]

    def _summary_sections(
        self,
        project: Project,
        *,
        user_context: str | None,
        unavailable_signals: list[str],
    ) -> dict[str, list[str]]:
        brief = project.brief
        sections = {
            "project_facts": [
                f"{project.project_name} là dự án {brief.property_segment.value} tại {brief.location}.",
                f"Khoảng giá: {brief.price_range}; nhóm mua chính: {brief.buyer_profile}.",
                "Điểm bán hàng chính: " + ", ".join(brief.key_selling_points[:5]) + ".",
            ],
            "local_context": [
                "Cần ưu tiên kiểm tra quy hoạch, kết nối giao thông, tiện ích và bối cảnh khu vực trước khi viết claim cụ thể.",
            ],
            "market_and_positioning": [
                f"Góc nghiên cứu nên nối mục tiêu {brief.campaign_objective} với buyer profile và mức giá {brief.price_range}.",
                "Research agent được phép dùng Google Search linh hoạt để tìm nguồn thị trường, địa phương và đối thủ phù hợp.",
            ],
            "assumptions_and_gaps": [
                "Chưa có kết quả Google Search cho bối cảnh địa phương, tín hiệu thị trường và định vị đối thủ.",
                f"Cần xử lý: {', '.join(unavailable_signals) if unavailable_signals else 'không có'}.",
            ],
            "next_step": [
                "Chuyển sang các research specialist dùng Google Search trước; chưa xác nhận insight và chưa chuyển sang Plan.",
            ],
        }
        if user_context:
            sections["market_and_positioning"].append(
                f"Ngữ cảnh người dùng cung cấp: {user_context}"
            )
        return sections

    def _brief_payload(self, project: Project) -> dict[str, Any]:
        return {
            "project_name": project.project_name,
            "property_segment": project.brief.property_segment.value,
            "location": project.brief.location,
            "price_range": project.brief.price_range,
            "key_selling_points": project.brief.key_selling_points,
            "campaign_objective": project.brief.campaign_objective,
            "buyer_profile": project.brief.buyer_profile,
            "tone": project.brief.tone,
            "promotion_details": project.brief.promotion_details,
        }
