from app.models.project import ProjectBriefCreate
from app.services.agent_workflow_service import AgentWorkflowService
from app.services.project_service import ProjectService


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


def test_collect_insight_workflow_runs_specialist_responsibilities(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv(
        "SQLITE_DATABASE_PATH", str(tmp_path / "content_creator.sqlite3")
    )
    project = ProjectService().create_project(ProjectBriefCreate(**_project_payload()))

    bundle = AgentWorkflowService().collect_insight_workflow(
        project.project_id,
        user_context="Metro line progress remains a major buyer interest point.",
        official_project_url="https://example.com/project",
    )

    assert bundle.project_id == project.project_id
    assert bundle.insight_snapshot_id
    assert bundle.insight_status == "partial"
    assert bundle.ready_for_confirmation is False
    assert len(bundle.questions) == 5
    assert "Tín hiệu nhu cầu nào phù hợp" in bundle.questions[1]
    assert bundle.approved_source_ids == []
    assert bundle.required_search_agents == [
        "local_context_agent",
        "market_research_agent",
        "competitor_positioning_agent",
    ]
    assert bundle.unavailable_signals == [
        "local context search not completed",
        "market signal search not completed",
        "competitor positioning search not completed",
    ]
    assert [task["agent"] for task in bundle.specialist_tasks] == [
        "project_fact_agent",
        "approved_source_search_agent",
        "local_context_agent",
        "market_research_agent",
        "competitor_positioning_agent",
    ]
    assert "project_facts" in bundle.summary_sections
    assert "market_and_positioning" in bundle.summary_sections
    assert bundle.project_facts["signals"][0]["signal_type"] == "project_fact"
    assert bundle.local_context["signals"]
    assert bundle.market_signals["signals"]
    assert bundle.competitor_positioning["signals"]
    assert (
        "Google Search is still required"
        in bundle.local_context["signals"][0]["summary"]
    )
    assert "Đã tạo insight snapshot" in bundle.insight_summary


def test_collect_insight_workflow_does_not_configure_source_ids(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv(
        "SQLITE_DATABASE_PATH", str(tmp_path / "content_creator.sqlite3")
    )
    project = ProjectService().create_project(ProjectBriefCreate(**_project_payload()))

    bundle = AgentWorkflowService().collect_insight_workflow(project.project_id)

    assert bundle.project_id == project.project_id
    assert bundle.insight_snapshot_id
    assert bundle.approved_source_ids == []
    assert bundle.ready_for_confirmation is False
    assert bundle.required_search_agents
    assert bundle.local_context["signals"]
    assert bundle.competitor_positioning["signals"]


def test_prepare_campaign_context_combines_strategy_and_plan(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv(
        "SQLITE_DATABASE_PATH", str(tmp_path / "content_creator.sqlite3")
    )
    project = ProjectService().create_project(ProjectBriefCreate(**_project_payload()))

    bundle = AgentWorkflowService().prepare_campaign_context(
        project.project_id,
        insight_snapshot_id="insight-123",
        insight_summary="Transit-oriented demand with verified local planning support.",
        planning_constraints={
            "total_budget_vnd": 120000000,
            "target_leads": 240,
            "campaign_days": 30,
        },
    )

    assert bundle.project_id == project.project_id
    assert bundle.insight_snapshot_id == "insight-123"
    assert bundle.strategy.rule_version == "campaign-strategy-v1"
    assert bundle.strategy.recommended_objective == "lead_generation"
    assert bundle.campaign_plan.rule_version == "campaign-planning-v1"
    assert bundle.campaign_plan.recommended_duration_days == 30
    assert bundle.campaign_plan.budget_band.unit == "VND"
