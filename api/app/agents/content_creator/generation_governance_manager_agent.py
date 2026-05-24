from google.adk.agents import Agent

from .instructions import (
    CONTENT_GENERATION_INSTRUCTION,
    GENERATION_GOVERNANCE_MANAGER_INSTRUCTION,
)
from .settings import get_agent_model
from .tools import assess_claim_risk, check_segment_constraints


content_generation_agent = Agent(
    model=get_agent_model(),
    name="content_generation_agent",
    description=(
        "Agent viết nội dung Facebook draft candidates. Dùng khi parent đã có saved "
        "brief, confirmed insight snapshot và Kogito-backed campaign_plan. Đầu vào "
        "là project facts, insight_summary, strategy decision, campaign_plan, tone và "
        "constraints. Trả về ít nhất 3 draft options kèm caption, angle, format, CTA, "
        "rationale, creative suggestion, review notes và risk-sensitive claims; không "
        "đánh dấu nội dung là approved."
    ),
    instruction=CONTENT_GENERATION_INSTRUCTION,
    tools=[assess_claim_risk, check_segment_constraints],
)


generation_governance_manager_agent = Agent(
    model=get_agent_model(),
    name="generation_governance_manager_agent",
    description=(
        "Manager điều phối generation và review governance. Dùng khi cần chuyển từ "
        "campaign_plan sang draft hoặc kiểm claim-risk/segment constraints. Đầu vào "
        "là project_id, brief, confirmed insight, campaign_plan và draft/review context. "
        "Trả về draft review-ready; không bỏ qua planning/insight gate."
    ),
    instruction=GENERATION_GOVERNANCE_MANAGER_INSTRUCTION,
    tools=[],
    sub_agents=[content_generation_agent],
)
