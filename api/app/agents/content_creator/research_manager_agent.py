from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools import AgentTool

from .instructions import (
    APPROVED_SOURCE_SEARCH_INSTRUCTION,
    COMPETITOR_POSITIONING_INSTRUCTION,
    LOCAL_CONTEXT_INSTRUCTION,
    MARKET_RESEARCH_INSTRUCTION,
    RESEARCH_MANAGER_INSTRUCTION,
)
from .settings import get_agent_model
from .tools import collect_insight_workflow, confirm_market_assumptions


approved_source_search_agent = Agent(
    model=get_agent_model(),
    name="approved_source_search_agent",
    description=(
        "Agent tìm kiếm nguồn web linh hoạt bằng ADK google_search. Dùng khi parent "
        "cần bằng chứng từ internet cho dự án, khu vực, thị trường, pháp lý, báo cáo "
        "hoặc tin tức liên quan. Đầu vào là câu hỏi nghiên cứu, project_name, location, "
        "property_segment, price_range hoặc URL gợi ý. Trả về nguồn có title, URL, "
        "publisher/date nếu có, tóm tắt liên quan và nhãn confidence; không viết bài."
    ),
    instruction=APPROVED_SOURCE_SEARCH_INSTRUCTION,
    tools=[google_search],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

local_context_agent = Agent(
    model=get_agent_model(),
    name="local_context_agent",
    description=(
        "Agent nghiên cứu bối cảnh địa phương. Dùng khi parent cần local planning "
        "and infrastructure, giao thông, tiện ích, quy hoạch, neighborhood context "
        "hoặc rủi ro claim theo location. Đầu vào là project_id nếu có, location, "
        "property_segment, key_selling_points và câu hỏi cần kiểm chứng. Trả về "
        "finding có URL, assumption/gap và cảnh báo claim vị trí; không biến tin "
        "quy hoạch/hạ tầng thành cam kết chắc chắn."
    ),
    instruction=LOCAL_CONTEXT_INSTRUCTION,
    tools=[google_search],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

market_research_agent = Agent(
    model=get_agent_model(),
    name="market_research_agent",
    description=(
        "Agent nghiên cứu thị trường và market insight questions. Dùng khi parent "
        "cần tín hiệu nhu cầu, buyer behavior, segment trends, pricing context hoặc "
        "content-angle opportunities cho location/property_segment. Đầu vào là brief, "
        "buyer_profile, campaign_objective, price_range và câu hỏi nghiên cứu. Trả về "
        "insight signals có nguồn, assumptions và câu hỏi cần người dùng xác nhận; "
        "không tự tính budget/KPI."
    ),
    instruction=MARKET_RESEARCH_INSTRUCTION,
    tools=[google_search],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

competitor_positioning_agent = Agent(
    model=get_agent_model(),
    name="competitor_positioning_agent",
    description=(
        "Agent nghiên cứu competitor positioning. Dùng khi parent cần so sánh dự án "
        "cùng khu vực/phân khúc, listing context, thông điệp đối thủ, khoảng giá và "
        "điểm khác biệt định vị. Đầu vào là location, property_segment, price_range, "
        "buyer_profile và key_selling_points. Trả về đối thủ/tín hiệu định vị có URL, "
        "differentiation opportunities và caveat; không coi listing là sự thật tuyệt đối."
    ),
    instruction=COMPETITOR_POSITIONING_INSTRUCTION,
    tools=[google_search],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)


research_manager_agent = Agent(
    model=get_agent_model(),
    name="research_manager_agent",
    description=(
        "Manager điều phối research và insight confirmation. Dùng sau khi đã có "
        "saved project_id để tạo hoặc refresh insight snapshot, giao việc cho các "
        "search specialists khi cần bằng chứng, và gom project facts, local context, "
        "market signals, competitor positioning, assumptions/gaps. Đầu vào là project_id "
        "thật và user_context/URL/tài liệu nếu có. Trả về insight_snapshot_id và bản "
        "tóm tắt cần user xác nhận; không chuyển sang planning khi insight chưa confirmed."
    ),
    instruction=RESEARCH_MANAGER_INSTRUCTION,
    tools=[collect_insight_workflow, 
        confirm_market_assumptions,
        AgentTool(agent=approved_source_search_agent),
        AgentTool(agent=local_context_agent),
        AgentTool(agent=market_research_agent),
        AgentTool(agent=competitor_positioning_agent)],
    sub_agents=[
        # approved_source_search_agent,
        # local_context_agent,
        # market_research_agent,
        # competitor_positioning_agent,
    ],
)
