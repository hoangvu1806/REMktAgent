from pathlib import Path

from google.adk.agents import Agent

from app.agents import (
    approved_source_search_agent,
    campaign_planning_agent,
    competitor_positioning_agent,
    content_generation_agent,
    content_creator_root_agent,
    generation_governance_manager_agent,
    intake_manager_agent,
    local_context_agent,
    market_research_agent,
    persona_strategy_agent,
    planning_manager_agent,
    project_fact_agent,
    research_manager_agent,
    root_agent,
)
from app.agents.content_creator.output_schemas import (
    ApprovedSourceSearchOutput,
    CompetitorPositioningOutput,
    LocalContextResearchOutput,
    MarketResearchOutput,
)


def test_root_agent_exports_domain_router() -> None:
    assert root_agent is content_creator_root_agent
    assert isinstance(root_agent, Agent)
    assert root_agent.name == "content_creator_root_agent"


def test_root_agent_registers_domain_manager_sub_agents() -> None:
    assert [agent.name for agent in root_agent.sub_agents] == [
        "intake_manager_agent",
        "research_manager_agent",
        "planning_manager_agent",
        "generation_governance_manager_agent",
    ]


def test_root_agent_is_router_only_without_project_mutation_tools() -> None:
    assert root_agent.tools == []


def test_manager_agents_register_expected_sub_agents_and_tools() -> None:
    assert [tool.__name__ for tool in intake_manager_agent.tools] == [
        "create_project",
        "get_project",
        "update_project",
    ]
    assert [agent.name for agent in intake_manager_agent.sub_agents] == [
        "project_fact_agent"
    ]

    assert [tool.__name__ for tool in research_manager_agent.tools[:2]] == [
        "collect_insight_workflow",
        "confirm_market_assumptions",
    ]
    assert [
        tool.agent.name
        for tool in research_manager_agent.tools[2:]
        if hasattr(tool, "agent")
    ] == [
        "approved_source_search_agent",
        "local_context_agent",
        "market_research_agent",
        "competitor_positioning_agent",
    ]
    assert research_manager_agent.sub_agents == []

    assert [tool.__name__ for tool in planning_manager_agent.tools] == [
        "prepare_campaign_context"
    ]
    assert [agent.name for agent in planning_manager_agent.sub_agents] == [
        "persona_strategy_agent",
        "campaign_planning_agent",
    ]

    assert generation_governance_manager_agent.tools == []
    assert [agent.name for agent in generation_governance_manager_agent.sub_agents] == [
        "content_generation_agent"
    ]


def test_agent_instructions_preserve_service_boundaries() -> None:
    for agent in [
        root_agent,
        intake_manager_agent,
        research_manager_agent,
        planning_manager_agent,
        generation_governance_manager_agent,
        project_fact_agent,
        local_context_agent,
        approved_source_search_agent,
        market_research_agent,
        competitor_positioning_agent,
        campaign_planning_agent,
        persona_strategy_agent,
        content_generation_agent,
    ]:
        assert "FastAPI" in agent.instruction
        assert "Kogito" in agent.instruction
        assert "Không được gọi trực tiếp Kogito" in agent.instruction


def test_agent_instructions_preserve_flexible_judgment_zones() -> None:
    assert "Luôn trả lời theo ngôn ngữ của người dùng" in root_agent.instruction
    assert "Agent xử lý ý định mơ hồ" in root_agent.instruction
    assert "Kogito-backed tools xử lý phần cần tính toán" in root_agent.instruction
    assert "Không tự tính budget, KPI, timing" in root_agent.instruction
    assert "Chọn câu hỏi và tín hiệu thật sự liên quan" in market_research_agent.instruction
    assert "Chọn field name/schema bằng tiếng Anh" not in root_agent.instruction
    assert "các field name/schema bằng tiếng Anh" not in root_agent.instruction
    assert "Có thể đề xuất nhiều cách hiểu hợp lý" in persona_strategy_agent.instruction
    assert "tạo ra ít nhất 3 phương án bài viết Facebook" in content_generation_agent.instruction
    assert "Giữ nguyên số liệu từ tool" in campaign_planning_agent.instruction


def test_manager_instructions_define_domain_routing_policies() -> None:
    assert "điều phối cấp cao" in root_agent.instruction
    assert "Luồng chuẩn" in root_agent.instruction
    assert "intake_manager_agent" in root_agent.instruction
    assert "Không dừng sau create_project" in root_agent.instruction
    assert "xác nhận insight" in root_agent.instruction
    assert "Tạo project ngay" in intake_manager_agent.instruction
    assert "dùng default hợp lý" in intake_manager_agent.instruction
    assert "update_project" in intake_manager_agent.instruction
    assert "data.project_id" in root_agent.instruction
    assert "brief campaign đầy đủ" in root_agent.instruction
    assert "Không hỏi \"có muốn tiếp tục không\"" in intake_manager_agent.instruction
    assert "Bạn xác nhận dùng các insight và assumptions này" in root_agent.instruction
    assert "Gọi collect_insight_workflow trước" in research_manager_agent.instruction
    assert "insight_snapshot_id" in research_manager_agent.instruction
    assert "ready_for_confirmation" in research_manager_agent.instruction
    assert "required_search_agents" in research_manager_agent.instruction
    assert "Không trả lời chỉ bằng câu hỏi" in research_manager_agent.instruction
    assert "bắt buộc hỏi người dùng xác nhận" in research_manager_agent.instruction
    assert "Bạn xác nhận dùng các insight và assumptions này" in research_manager_agent.instruction
    assert '"viết bài"' in research_manager_agent.instruction
    assert "Không được gọi confirm_market_assumptions" in research_manager_agent.instruction
    assert "Không được bàn giao sang planning_manager_agent" in research_manager_agent.instruction
    assert "theo nghiên cứu thị trường thì sao" in research_manager_agent.instruction
    assert "một câu ngắn" in research_manager_agent.instruction
    assert "confirm_market_assumptions" in research_manager_agent.instruction
    assert "planning_manager_agent" in research_manager_agent.instruction
    assert "source-backed" in research_manager_agent.instruction
    assert "prepare_campaign_context là boundary chính" in planning_manager_agent.instruction
    assert "generation_governance_manager_agent" in planning_manager_agent.instruction
    assert "Kogito-backed output" in planning_manager_agent.instruction
    assert "rule_version" in planning_manager_agent.instruction
    assert "content_generation_agent" in generation_governance_manager_agent.instruction
    assert "draft/review persistence chưa được triển khai" in generation_governance_manager_agent.instruction
    assert "chưa có review status rõ ràng" in generation_governance_manager_agent.instruction


def test_agent_descriptions_define_parent_routing_contracts() -> None:
    for agent in [
        root_agent,
        intake_manager_agent,
        research_manager_agent,
        planning_manager_agent,
        generation_governance_manager_agent,
        project_fact_agent,
        local_context_agent,
        approved_source_search_agent,
        market_research_agent,
        competitor_positioning_agent,
        campaign_planning_agent,
        persona_strategy_agent,
        content_generation_agent,
    ]:
        assert "Dùng" in agent.description or "Dùng khi" in agent.description
        assert "Đầu vào" in agent.description
        assert "Trả về" in agent.description

    assert "saved project_id" in research_manager_agent.description
    assert "insight_snapshot_id" in research_manager_agent.description
    assert "google_search" in approved_source_search_agent.description
    assert "local planning and infrastructure" in local_context_agent.description
    assert "market insight questions" in market_research_agent.description
    assert "competitor positioning" in competitor_positioning_agent.description
    assert "budget, KPI, and timing" in campaign_planning_agent.description
    assert "campaign metrics" in persona_strategy_agent.description
    assert "Facebook draft candidates" in content_generation_agent.description


def test_specialists_register_allowlisted_internal_tools() -> None:
    assert [tool.__name__ for tool in project_fact_agent.tools] == [
        "collect_project_facts",
    ]
    for agent in [
        approved_source_search_agent,
        local_context_agent,
        market_research_agent,
        competitor_positioning_agent,
    ]:
        assert [tool.name for tool in agent.tools] == ["google_search"]
    assert [tool.__name__ for tool in campaign_planning_agent.tools] == [
        "evaluate_campaign_plan",
        "calculate_budget_forecast",
        "recommend_campaign_timeline",
    ]
    assert [tool.__name__ for tool in persona_strategy_agent.tools] == [
        "evaluate_campaign_strategy",
        "check_segment_constraints",
    ]


def test_campaign_planning_agent_does_not_calculate_metrics_by_prompt() -> None:
    assert "Không tự tính budget_band" in campaign_planning_agent.instruction
    assert "Kogito-backed tools" in campaign_planning_agent.instruction


def test_adk_builtin_search_agent_is_isolated_from_custom_tools() -> None:
    for agent in [
        approved_source_search_agent,
        local_context_agent,
        market_research_agent,
        competitor_positioning_agent,
    ]:
        assert len(agent.tools) == 1
        assert agent.tools[0].name == "google_search"
        assert agent.disallow_transfer_to_parent is True
        assert agent.disallow_transfer_to_peers is True
    assert "không phụ thuộc hard-coded source catalog" in approved_source_search_agent.instruction
    assert all(
        getattr(tool, "name", None) != "google_search"
        for tool in research_manager_agent.tools
    )
    assert [tool.__name__ for tool in content_generation_agent.tools] == [
        "assess_claim_risk",
        "check_segment_constraints",
    ]


def test_research_specialists_use_prompt_contract_not_adk_output_schema() -> None:
    for agent in [
        approved_source_search_agent,
        local_context_agent,
        market_research_agent,
        competitor_positioning_agent,
    ]:
        assert agent.output_schema is None
        assert "research output contract" in agent.instruction

    # Keep Pydantic contracts available for documentation, tests, and future
    # non-search normalizers, but do not attach them to google_search agents.
    assert ApprovedSourceSearchOutput.model_json_schema()["properties"].keys() >= {
        "sources",
        "findings",
        "unavailable_signals",
    }
    assert LocalContextResearchOutput.model_json_schema()["properties"].keys() >= {
        "local_planning_and_infrastructure",
        "transport_and_amenities",
        "sources",
        "gaps",
    }
    assert MarketResearchOutput.model_json_schema()["properties"].keys() >= {
        "research_questions",
        "demand_signals",
        "content_angle_opportunities",
        "sources",
    }
    assert CompetitorPositioningOutput.model_json_schema()["properties"].keys() >= {
        "competitor_signals",
        "positioning_patterns",
        "differentiation_opportunities",
        "sources",
    }


def test_agent_instructions_are_runtime_prompts_not_dev_docs() -> None:
    for agent in [
        root_agent,
        intake_manager_agent,
        research_manager_agent,
        planning_manager_agent,
        generation_governance_manager_agent,
        project_fact_agent,
        local_context_agent,
        approved_source_search_agent,
        market_research_agent,
        competitor_positioning_agent,
        campaign_planning_agent,
        persona_strategy_agent,
        content_generation_agent,
    ]:
        assert "Vai trò:" in agent.instruction
    assert "Epic" not in agent.instruction
    assert "FR" not in agent.instruction


def test_adk_web_runtime_disables_progressive_sse_streaming() -> None:
    env_example = Path(__file__).resolve().parents[1] / ".env.example"

    assert "ADK_DISABLE_PROGRESSIVE_SSE_STREAMING=true" in env_example.read_text()
