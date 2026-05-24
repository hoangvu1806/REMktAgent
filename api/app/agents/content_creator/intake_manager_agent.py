from google.adk.agents import Agent

from .instructions import INTAKE_MANAGER_INSTRUCTION, PROJECT_FACT_INSTRUCTION
from .settings import get_agent_model
from .tools import (
    collect_project_facts,
    create_project,
    get_project,
    update_project,
)

project_fact_agent = Agent(
    model=get_agent_model(),
    name="project_fact_agent",
    description=(
        "Agent chuẩn hóa project facts. Dùng khi cần trích xuất và kiểm tra thông "
        "tin dự án từ brief, official_project_url hoặc user_material_refs. Đầu vào "
        "gồm project_id, brief_json, tài liệu/URL nếu có. Trả về facts có nguồn, "
        "missing fields và sensitive claims; không tự bịa thông tin chưa có."
    ),
    instruction=PROJECT_FACT_INSTRUCTION,
    tools=[collect_project_facts],
)

intake_manager_agent = Agent(
    model=get_agent_model(),
    name="intake_manager_agent",
    description=(
        "Manager tiếp nhận và lưu project brief. Dùng khi người dùng cung cấp dự án "
        "mới, muốn sửa brief, tải lại project_id, hoặc cần kiểm tra generation-ready. "
        "Đầu vào là project brief tự nhiên hoặc project_id. Trả về saved project với "
        "project_id thật và quyết định hỏi bổ sung hay chuyển sang research; không "
        "làm market research, planning hoặc viết bài."
    ),
    instruction=INTAKE_MANAGER_INSTRUCTION,
    tools=[create_project, get_project, update_project],
    sub_agents=[project_fact_agent],
)
