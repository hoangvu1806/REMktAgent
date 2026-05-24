from google.adk.agents import Agent

from .generation_governance_manager_agent import generation_governance_manager_agent
from .instructions import COORDINATOR_INSTRUCTION
from .intake_manager_agent import intake_manager_agent
from .planning_manager_agent import planning_manager_agent
from .research_manager_agent import research_manager_agent
from .settings import get_agent_model


content_creator_root_agent = Agent(
    model=get_agent_model(),
    name="content_creator_root_agent",
    description=(
        "Agent điều phối cấp cao của workflow tạo nội dung bất động sản. "
        "Dùng khi cần xác định bước tiếp theo trong luồng từ intake, research, "
        "confirmation, planning, generation đến review. Đầu vào là user intent, "
        "project_id nếu có, và trạng thái hội thoại hiện tại. Trả về việc chuyển "
        "giao cho manager phù hợp; không tự xử lý thay specialist."
    ),
    instruction=COORDINATOR_INSTRUCTION,
    tools=[],
    sub_agents=[
        intake_manager_agent,
        research_manager_agent,
        planning_manager_agent,
        generation_governance_manager_agent,
    ],
)

# ADK project entrypoint expected by adk run/adk web style tooling.
root_agent = content_creator_root_agent
