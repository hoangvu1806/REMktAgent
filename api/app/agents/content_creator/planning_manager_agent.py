from google.adk.agents import Agent

from .instructions import (
    CAMPAIGN_PLANNING_INSTRUCTION,
    PERSONA_STRATEGY_INSTRUCTION,
    PLANNING_MANAGER_INSTRUCTION,
)
from .settings import get_agent_model
from .tools import (
    calculate_budget_forecast,
    check_segment_constraints,
    evaluate_campaign_plan,
    evaluate_campaign_strategy,
    prepare_campaign_context,
    recommend_campaign_timeline,
)


persona_strategy_agent = Agent(
    model=get_agent_model(),
    name="persona_strategy_agent",
    description=(
        "Agent chiến lược persona và CTA. Dùng khi parent cần diễn giải confirmed "
        "brief + confirmed insight thành target persona, objective, CTA candidates, "
        "segment constraints và rule evaluation inputs. Đầu vào là project brief, "
        "insight_snapshot_id/insight_summary và planning assumptions. Trả về strategy "
        "context cho Kogito-backed tools; không tự tính campaign metrics."
    ),
    instruction=PERSONA_STRATEGY_INSTRUCTION,
    tools=[evaluate_campaign_strategy, check_segment_constraints],
)


campaign_planning_agent = Agent(
    model=get_agent_model(),
    name="campaign_planning_agent",
    description=(
        "Agent lập kế hoạch campaign bằng Kogito-backed tools. Dùng khi parent cần "
        "budget, KPI, and timing sau khi đã có confirmed insight và strategy context. "
        "Đầu vào là project_id, brief, insight_summary, constraints, target_leads hoặc "
        "budget nếu có. Trả về budget bands, KPI forecast, CPL assumptions, timeline, "
        "cadence, rule_version và formula_version; không tự tính số liệu bằng prompt."
    ),
    instruction=CAMPAIGN_PLANNING_INSTRUCTION,
    tools=[
        evaluate_campaign_plan,
        calculate_budget_forecast,
        recommend_campaign_timeline,
    ],
)


planning_manager_agent = Agent(
    model=get_agent_model(),
    name="planning_manager_agent",
    description=(
        "Manager điều phối planning. Dùng sau khi insight đã được user confirm để "
        "chuẩn bị campaign context, strategy decision, objective, CTA, ngân sách, KPI, "
        "timing và approval logic. Đầu vào là project_id, insight_snapshot_id hoặc "
        "confirmed insight_summary, planning_constraints và unavailable_signals. Trả "
        "về campaign_plan Kogito-backed cho generation; không làm research hoặc viết bài."
    ),
    instruction=PLANNING_MANAGER_INSTRUCTION,
    tools=[prepare_campaign_context],
    sub_agents=[persona_strategy_agent, campaign_planning_agent],
)
