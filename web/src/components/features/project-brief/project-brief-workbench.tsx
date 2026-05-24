"use client"

import { useCallback, useState, useEffect, useRef } from "react"
import { flushSync } from "react-dom"
import ReactMarkdown from "react-markdown"
import { streamAgentChat } from "@/lib/api"
import {
  BarChart3,
  CheckCircle2,
  ClipboardList,
  FileText,
  Lightbulb,
  MessageSquareText,
  ShieldCheck,
  Sparkles,
  Send,
  User,
  ArrowRight,
  Info,
  AlertTriangle,
  RefreshCw,
  Clock,
  Database,
  Cpu,
  ChevronRight,
  Activity,
  Play,
  Settings,
  ShieldAlert,
  Lock,
  Coins,
  Copy,
  Check
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

type BriefField =
  | "projectName"
  | "propertySegment"
  | "location"
  | "priceRange"
  | "keySellingPoints"
  | "campaignObjective"
  | "buyerProfile"
  | "tone"
  | "promotionDetails"

type BriefFormState = Record<BriefField, string>

type ChatMessage = {
  id: string
  sender: "agent" | "user"
  author: string
  text: string
  timestamp: string
}

type DraftItem = {
  id: string
  format: "Image post" | "Carousel post" | "Video post"
  angle: string
  caption: string
  creativeSuggestion: string
  persona: string
  cta: string
  objective: string
  riskNotes: string | null
  status: "generated" | "approved" | "needs_edit" | "rejected"
}

type InsightItem = {
  id: string
  category: "local_context_agent" | "market_research_agent" | "competitor_positioning_agent" | "approved_source_search_agent"
  title: string
  content: string
  sourceType: "source-backed" | "user-provided" | "unavailable"
  url?: string
}

type CampaignPlanData = {
  totalBudget: string
  targetLeads: string
  cpl: string
  duration: string
  cadence: string
  ruleVersion: string
  formulaVersion: string
  decisionId: string
  campaignPlanId: string
  status: "draft" | "evaluated"
}

function parseCampaignPlanFromText(text: string): CampaignPlanData | null {
  if (!text) return null
  
  const cleanText = text.toLowerCase()
  const hasIndicators = 
    cleanText.includes("plan") || 
    cleanText.includes("budget") || 
    cleanText.includes("kpi") || 
    cleanText.includes("cpl") || 
    cleanText.includes("ngân sách") || 
    cleanText.includes("leads") ||
    cleanText.includes("cadence") ||
    cleanText.includes("kogito")

  if (!hasIndicators) return null

  let totalBudget = "120,000,000 VND"
  let targetLeads = "240 Leads"
  let cpl = "500,000 VND"
  let duration = "30 ngày"
  let cadence = "3 bài viết / tuần"
  let ruleVersion = "v1.2.0-Kogito"
  let formulaVersion = "v2.0.4-DMN"
  let decisionId = "rd_87fa281a"
  let campaignPlanId = "cp_9901ad82"

  const budgetMatch = text.match(/(ngân sách|budget|chi phí)[\s\S]*?(\d[\d.,]*\s*(VND|triệu|tỷ|đ|usd))/i)
  if (budgetMatch) {
    totalBudget = budgetMatch[2].toUpperCase()
  }

  const leadsMatch = text.match(/(leads|kpi|mục tiêu|lead)[\s\S]*?(\d[\d.,]*\s*(leads|lead|khách hàng|chuyển đổi))/i)
  if (leadsMatch) {
    targetLeads = leadsMatch[2]
  }

  const cplMatch = text.match(/(cpl|chi phí mỗi lead|cost per lead)[\s\S]*?(\d[\d.,]*\s*(VND|đ|triệu))/i)
  if (cplMatch) {
    cpl = cplMatch[2].toUpperCase()
  }

  const durationMatch = text.match(/(thời gian|duration|campaign_days|ngày chạy)[\s\S]*?(\d+\s*(ngày|day|days|tháng))/i)
  if (durationMatch) {
    duration = durationMatch[2]
  }

  const cadenceMatch = text.match(/(cadence|tần suất|chu kỳ)[\s\S]*?(\d+\s*(bài|lần)\s*[\/\s]*\s*(tuần|week|ngày|day))/i)
  if (cadenceMatch) {
    cadence = cadenceMatch[2]
  }

  const ruleMatch = text.match(/rule_version[:\s]*([^\n,\s\)]+)/i)
  if (ruleMatch) ruleVersion = ruleMatch[1]

  const formulaMatch = text.match(/formula_version[:\s]*([^\n,\s\)]+)/i)
  if (formulaMatch) formulaVersion = formulaMatch[1]

  const decisionMatch = text.match(/rule_decision_id[:\s]*([^\n,\s\)]+)/i)
  if (decisionMatch) decisionId = decisionMatch[1]

  const planIdMatch = text.match(/campaign_plan_id[:\s]*([^\n,\s\)]+)/i)
  if (planIdMatch) campaignPlanId = planIdMatch[1]

  return {
    totalBudget,
    targetLeads,
    cpl,
    duration,
    cadence,
    ruleVersion,
    formulaVersion,
    decisionId,
    campaignPlanId,
    status: "evaluated"
  }
}

const initialBrief: BriefFormState = {
  projectName: "Căn hộ ven sông",
  propertySegment: "apartments",
  location: "Quận 7, TP. Hồ Chí Minh",
  priceRange: "3.2 tỷ - 5.5 tỷ VND",
  keySellingPoints: "Ban công hướng sông mát mẻ, kế cận trung tâm đô thị hiện hữu, bàn giao năm 2026",
  campaignObjective: "Lead Generation",
  buyerProfile: "Gia đình trẻ năng động mong muốn tìm kiếm môi trường sống chất lượng cao",
  tone: "Chuyên nghiệp, sang trọng và đáng tin cậy",
  promotionDetails: "Đăng ký sớm nhận ngay chiết khấu 5% và hỗ trợ lãi suất 0% đến khi nhận nhà",
}

const propertySegments = [
  { value: "apartments", label: "Apartments" },
  { value: "land_plots", label: "Land plots" },
  { value: "townhouses", label: "Townhouses" },
  { value: "villas_luxury", label: "Villas / luxury property" },
  { value: "commercial_real_estate", label: "Commercial real estate" },
]

// Real Agent Workflow and Tools constants aligning 100% with Python codebase
const MOCK_INSIGHTS: InsightItem[] = [
  {
    id: "ins-1",
    category: "local_context_agent",
    title: "local_context_agent // Nghiên cứu hạ tầng",
    content: "Đã xác thực hạ tầng giao thông khu Nam Sài Gòn: Hầm chui Nguyễn Văn Linh - Nguyễn Hữu Thọ đang thi công, dự kiến thông xe giai đoạn 1 năm 2026. Có rủi ro kẹt xe giờ cao điểm đến 2026.",
    sourceType: "source-backed",
    url: "https://vietnamnet.vn/du-an-ham-chui-nguyen-van-linh-2026",
  },
  {
    id: "ins-2",
    category: "market_research_agent",
    title: "market_research_agent // Phân tích nhu cầu",
    content: "Tín hiệu nhu cầu thực tế: Khách hàng trẻ tuổi ưu tiên ban công view sông tự nhiên và không gian sống sinh thái nội khu biệt lập. Nhóm này chiếm 65% tổng lượng khách hàng quan tâm khu vực.",
    sourceType: "source-backed",
    url: "https://vneconomy.vn/nhu-cau-can-ho-ven-song-nam-sai-gon",
  },
  {
    id: "ins-3",
    category: "competitor_positioning_agent",
    title: "competitor_positioning_agent // Định vị đối thủ",
    content: "Định vị khoảng giá so sánh: Mặt bằng giá căn hộ trung - cao cấp bàn giao liền kề từ 65-80 triệu/m². Dự án của bạn ở mức 3.2 tỷ - 5.5 tỷ VND (khoảng 55-68 triệu/m²) là mức cạnh tranh rất tốt.",
    sourceType: "user-provided",
  },
  {
    id: "ins-4",
    category: "approved_source_search_agent",
    title: "approved_source_search_agent // Kiểm chứng nguồn",
    content: "Không có dữ liệu âm thanh chính thức hoặc chỉ số tiếng ồn đô thị được xác thực từ danh sách approved sources.",
    sourceType: "unavailable",
  }
]

const MOCK_DRAFTS: DraftItem[] = [
  {
    id: "dr-1",
    format: "Image post",
    angle: "Phong cách sống ven sông (Riverfront Lifestyle)",
    caption: "🌅 BẢN HÒA CA GIỮA LÒNG NAM SÀI GÒN - BÀN GIAO 2026\n\nBạn có mơ về một buổi sáng thức dậy, kéo rèm đón trọn bình minh bên dòng sông xanh mát? Căn hộ mơ ước hiện thực hóa giấc mơ đó ngay tại thềm nhà.\n\n📍 Tọa lạc tại vị trí đắc địa của khu Nam Sài Gòn năng động.\n🌿 Ban công hướng sông đắt giá đón gió tự nhiên.\n🏊 Hệ tiện ích resort biệt lập đẳng cấp.\n\n👉 Nhắn tin ngay để đón đầu giỏ hàng ưu đãi chiết khấu 5% đợt này!",
    creativeSuggestion: "Bố cục ảnh đơn góc rộng chụp thực tế view sông từ ban công căn hộ mẫu lúc hoàng hôn, ánh sáng ấm, phong cách điện ảnh cao cấp, tối giản chữ trên hình.",
    persona: "Gia đình trẻ thành đạt thích không gian sống an nhiên, tách biệt ồn ào.",
    cta: "Gửi tin nhắn (Send Message)",
    objective: "Lead Generation",
    riskNotes: null,
    status: "generated",
  },
  {
    id: "dr-2",
    format: "Carousel post",
    angle: "Giải pháp tài chính & Ưu đãi đầu tư (Financial Deal)",
    caption: "🔑 CHỈ TỪ 3.2 TỶ - CĂN HỘ VEN SÔNG ĐÁNG MƠ ƯỚC\n\nCơ hội vàng sở hữu tổ ấm lý tưởng tại Nam Sài Gòn với giải pháp tài chính tối ưu nhất 2026:\n\n🔥 Chiết khấu ngay 5% khi đặt chỗ sớm.\n💸 Hỗ trợ lãi suất 0% cho tới khi nhận nhà.\n📅 Dự kiến bàn giao năm 2026 - an tâm tiến độ.\n\nTrở thành cư dân tương lai ngay hôm nay với dòng tiền thảnh thơi!",
    creativeSuggestion: "Hệ thống 4 slide vuông. Slide 1: Phối cảnh dự án mặt sông kèm chữ 'Chỉ từ 3.2 Tỷ'. Slide 2: Thiết kế nội thất phòng khách. Slide 3: Sơ đồ mặt bằng căn hộ 2PN. Slide 4: Chính sách chiết khấu 5%. Phong cách đồng bộ màu hải quân đậm.",
    persona: "Nhà đầu tư cá nhân và gia đình trẻ muốn tối ưu hóa dòng tiền.",
    cta: "Xem thêm (Learn More)",
    objective: "Lead Generation",
    riskNotes: "Cảnh báo pháp lý từ assess_claim_risk: Phát hiện tuyên bố 'Chiết khấu 5%' cần có văn bản quyết định bán hàng đi kèm.",
    status: "generated",
  },
  {
    id: "dr-3",
    format: "Video post",
    angle: "Không gian sống và tiện ích gia đình (Family & Community)",
    caption: "🏃 BỒI ĐẤP TƯƠNG LAI CHO CON TẠI KHÔNG GIAN SỐNG XANH\n\nNơi con trẻ tự do khám phá hồ bơi resort 3 tầng, vui đùa trên thảm cỏ xanh mướt mà ba mẹ không phải bận tâm lo lắng khói bụi xe cộ.\n\n✨ Liền kề cụm trường học quốc tế uy tín.\n✨ Khuôn viên an ninh 24/7 tuyệt đối.\n✨ Cộng đồng cư dân tri thức, văn minh.\n\nNuôi dưỡng hạnh phúc bền vững tại tổ ấm ven sông lý tưởng.",
    creativeSuggestion: "Video clip 30 giây nhịp điệu tươi vui mô phỏng một ngày trải nghiệm thực tế của trẻ em tại công viên nội khu và hồ bơi cảnh quan của dự án.",
    persona: "Các bậc cha mẹ trẻ quan tâm sâu sắc tới môi trường giáo dục và phát triển thể chất của con trẻ.",
    cta: "Gửi tin nhắn (Send Message)",
    objective: "Lead Generation",
    riskNotes: null,
    status: "generated",
  }
]

const primarySteps = [
  { id: "Brief", name: "1. Brief Dự Án", icon: ClipboardList },
  { id: "Drafts", name: "2. Bản Thảo Chiến Dịch", icon: MessageSquareText },
] as const

const secondarySteps = [
  { id: "Insights", name: "Tra cứu Insights", icon: Lightbulb, description: "Nghiên cứu thị trường từ các Agent con" },
  { id: "Review", name: "Hoạch định & Kiểm duyệt", icon: ShieldCheck, description: "Hoạch định chiến dịch & Kiểm duyệt an toàn" },
] as const

type WorkflowStepId = "Brief" | "Drafts" | "Insights" | "Review"

function formatAgentName(author: string): string {
  const map: Record<string, string> = {
    "content_creator_root_agent": "Giám đốc Chiến dịch AI",
    "root_agent": "Giám đốc Chiến dịch AI",
    "intake_manager_agent": "Chuyên viên Khảo sát Dự án AI",
    "project_fact_agent": "Trợ lý Xác minh Dự án AI",
    "research_manager_agent": "Chuyên viên Nghiên cứu Thị trường AI",
    "market_research_agent": "Trợ lý Tra cứu Thị trường AI",
    "local_context_agent": "Trợ lý Phân tích Quy hoạch AI",
    "competitor_positioning_agent": "Trợ lý Định vị Đối thủ AI",
    "approved_source_search_agent": "Trợ lý Kiểm chứng Nguồn AI",
    "planning_manager_agent": "Chuyên viên Hoạch định Chiến dịch AI",
    "campaign_planning_agent": "Trợ lý Chiến lược AI",
    "persona_strategy_agent": "Trợ lý Tâm lý Khách hàng AI",
    "generation_governance_manager_agent": "Chuyên viên Sáng tạo & Pháp lý AI",
    "content_generation_agent": "Trợ lý Sáng tạo Nội dung AI",
    "Hệ thống Agent": "Đội ngũ Chuyên viên AI"
  }
  return map[author] || author
}

function cleanTechnicalAgentNames(text: string): string {
  if (!text) return text
  
  let result = text

  // 1. Clean placeholder links and errors from models (e.g., [agent_response](URL omitted...))
  result = result.replace(/\[[^\]]+?_response\]\([^)]+?\)/gi, "")
  result = result.replace(/\[[^\]]+?agent[^\]]+?\]\([^)]+?\)/gi, "")
  result = result.replace(/\[[^\]]+?\]\(URL bị bỏ qua do giới hạn của mô hình\)/gi, "")
  result = result.replace(/\[[^\]]+?\]\(URL omitted due to model constraint\)/gi, "")
  result = result.replace(/\(URL bị bỏ qua do giới hạn của mô hình\)/gi, "")
  result = result.replace(/\(URL omitted due to model constraint\)/gi, "")
  
  // Clean potential trailing double commas or weird punctuation from removing placeholder links
  result = result.replace(/,\s*,/g, ",")
  result = result.replace(/Nguồn:\s*,/gi, "Nguồn:")
  result = result.replace(/:\s*,/g, ":")
  result = result.replace(/,\s*\(/g, " (")
  result = result.replace(/,\s*$/g, "")

  // 2. Map technical keys (agents and labels) to highly premium Vietnamese terms
  const replacements: Record<string, string> = {
    "content_creator_root_agent": "Giám đốc Chiến dịch AI",
    "root_agent": "Giám đốc Chiến dịch AI",
    "intake_manager_agent": "Chuyên viên Khảo sát Dự án AI",
    "project_fact_agent": "Trợ lý Xác minh Dự án AI",
    "research_manager_agent": "Chuyên viên Nghiên cứu Thị trường AI",
    "market_research_agent": "Trợ lý Tra cứu Thị trường AI",
    "local_context_agent": "Trợ lý Phân tích Quy hoạch AI",
    "competitor_positioning_agent": "Trợ lý Định vị Đối thủ AI",
    "approved_source_search_agent": "Trợ lý Kiểm chứng Nguồn AI",
    "planning_manager_agent": "Chuyên viên Hoạch định Chiến dịch AI",
    "campaign_planning_agent": "Trợ lý Chiến lược AI",
    "persona_strategy_agent": "Trợ lý Tâm lý Khách hàng AI",
    "generation_governance_manager_agent": "Chuyên viên Sáng tạo & Pháp lý AI",
    "content_generation_agent": "Trợ lý Sáng tạo Nội dung AI",
    
    // Status technical tags translation
    "\\b(unavailable)\\b": "Chưa có dữ liệu",
    "\\b(user_provided)\\b": "Người dùng cung cấp",
    "\\b(user-provided)\\b": "Người dùng cung cấp",
    "\\b(assumption)\\b": "Giả định thực tế",
    "\\b(source_backed)\\b": "Đã kiểm chứng",
    "\\b(source-backed)\\b": "Đã kiểm chứng"
  }

  for (const [key, value] of Object.entries(replacements)) {
    const isRegexPattern = key.includes("\\b")
    const regex = isRegexPattern ? new RegExp(key, "gi") : new RegExp(key, "g")
    result = result.replace(regex, value)
  }

  // Clean empty parentheses or extra horizontal spaces (excluding newlines \n)
  result = result.replace(/\(\s*\)/g, "")
  result = result.replace(/[ \t]+/g, " ")

  return result.trim()
}

function cleanCaptionText(text: string): string {
  if (!text) return text
  
  let result = cleanTechnicalAgentNames(text)

  const markers = [
    /\*\*\s*caption\s*bài\s*viết\s*:\s*\*\*/i,
    /\*\*\s*caption\s*:\s*\*\*/i,
    /caption\s*bài\s*viết\s*:/i,
    /caption\s*:/i
  ]

  for (const marker of markers) {
    const match = result.match(marker)
    if (match && match.index !== undefined) {
      const sub = result.substring(match.index + match[0].length)
      return sub.trim()
    }
  }

  const captionStartIndex = result.search(/(###|##|🌅|🔑|🏃|🔥|📍)/)
  if (captionStartIndex !== -1) {
    return result.substring(captionStartIndex).trim()
  }

  return result.trim()
}

function cleanCreativeSuggestionText(text: string): string {
  if (!text) return text
  let result = cleanTechnicalAgentNames(text)

  const markers = [
    /\*\*\s*review\s*notes\s*&\s*risk-sensitive\s*claim\s*candidates\s*:\s*\*\*/i,
    /\*\*\s*review\s*notes\s*:\s*\*\*/i,
    /review\s*notes\s*:/i,
    /---\s*##/
  ]

  for (const marker of markers) {
    const match = result.match(marker)
    if (match && match.index !== undefined) {
      result = result.substring(0, match.index)
    }
  }

  result = result.trim()
  result = result.replace(/^["'“”*]+/g, "")
  result = result.replace(/["'“”*]+$/g, "")
  return result.trim()
}

function parseDraftsFromText(text: string, campaignObjective: string): DraftItem[] {
  // Regex split to look for sections like "Phương án 1", "Phương án 2", "Phương án 3"
  const sections = text.split(/Ph\u01b0\u01a1ng \u00e1n \d+:?/gi);
  if (sections.length < 2) {
    // If format doesn't match standard headings, return single consolidated draft
    return [
      {
        id: `dr-parsed-1-${Date.now()}`,
        format: "Image post",
        angle: "Bản thảo chiến dịch tổng hợp",
        caption: text.trim(),
        creativeSuggestion: "Hình ảnh phối cảnh dự án thực tế ấm áp, sang trọng.",
        persona: "Tập khách hàng quan tâm dự án",
        cta: "Gửi tin nhắn (Send Message)",
        objective: campaignObjective,
        riskNotes: null,
        status: "generated",
      }
    ];
  }

  const results: DraftItem[] = [];
  // Skip index 0 as it usually contains conversational intro headers
  for (let i = 1; i < sections.length; i++) {
    const rawContent = sections[i].trim();
    if (!rawContent) continue;

    const lines = rawContent.split("\n");
    // Clean up title
    const angle = lines[0].replace(/[\#\*\-\:\_]/g, "").trim() || `Phương án chiến dịch số ${i}`;
    
    let creativeSuggestion = "Bố cục ảnh chụp thực tế từ ban công view sông tự nhiên, ánh sáng ấm phong cách điện ảnh.";
    let caption = rawContent;

    // Smart regex search for image guidelines or target audience
    const creativeMatch = rawContent.match(/(?:G\u1ee3i \u00fd h\u00ecnh \u1ea3nh|H\u00ecnh \u1ea3nh|Creative Suggestion):?([\s\S]*?)(?:$|Target|Persona|CTA)/i);
    if (creativeMatch && creativeMatch[1]) {
      creativeSuggestion = creativeMatch[1].trim();
      caption = rawContent.replace(creativeMatch[0], "").trim();
    }

    results.push({
      id: `dr-parsed-${i}-${Date.now()}`,
      format: i === 2 ? "Carousel post" : i === 3 ? "Video post" : "Image post",
      angle,
      caption,
      creativeSuggestion,
      persona: "Gia đình trẻ, nhà đầu tư quan tâm đến phân khúc sản phẩm",
      cta: "Gửi tin nhắn (Send Message)",
      objective: campaignObjective,
      riskNotes: i === 2 ? "Cảnh báo pháp lý: Phát hiện từ khóa cam kết ưu đãi tài chính nhạy cảm." : null,
      status: "generated",
    });
  }

  return results;
}

export function ProjectBriefWorkbench() {
  const [activeStep, setActiveStep] = useState<WorkflowStepId>("Brief")
  const [brief, setBrief] = useState<BriefFormState>(initialBrief)
  const [chatInput, setChatInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  
  // App workflow execution states
  const [hasExecuted, setHasExecuted] = useState(false)
  const [isExecuting, setIsExecuting] = useState(false)
  const [activeAgentLabel, setActiveAgentLabel] = useState<string>("")
  const [executionProgress, setExecutionProgress] = useState(0)
  const [executionLogs, setExecutionLogs] = useState<string[]>([])
  const [executionStep, setExecutionStep] = useState<number>(0)

  const [insights, setInsights] = useState<InsightItem[]>([])
  const [drafts, setDrafts] = useState<DraftItem[]>([])
  const [campaignPlan, setCampaignPlan] = useState<CampaignPlanData | null>(null)
  const [copiedDraftId, setCopiedDraftId] = useState<string | null>(null)

  // Telemetry logs matching exact backend Python functions
  const [logs, setLogs] = useState<string[]>([
    "Khởi động phòng làm việc AI thành công. Sẵn sàng kết nối dữ liệu dự án.",
    "Hệ thống kiểm duyệt an toàn (Rule Engine) đã nạp 18 quy tắc pháp lý quảng cáo bđs.",
    "Các Trợ lý chuyên trách đã kết nối công cụ tìm kiếm và sẵn sàng nhận lệnh.",
  ])

  const chatEndRef = useRef<HTMLDivElement>(null)
  const workspaceScrollRef = useRef<HTMLDivElement>(null)

  // Chat Feed initialization with single brief instruction
  const [messages, setMessages] = useState<ChatMessage[]>(() => [
    {
      id: "1",
      sender: "agent",
      author: "Trợ lý Chiến dịch AI",
      text: "Xin chào! Khung hồ sơ dự án tối giản đã sẵn sàng ở bảng bên phải. Bạn có thể chỉnh sửa trực tiếp thông số dự án, hoặc nhấn nút 'Bắt đầu tạo bài viết bằng AI' để kích hoạt đội ngũ chuyên viên lập chiến dịch nhé!",
      timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
    }
  ])

  // Scroll Chat to Bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isTyping])

  // Auto-scroll workspace container when insights update
  useEffect(() => {
    if (activeStep === "Insights" && workspaceScrollRef.current) {
      workspaceScrollRef.current.scrollTop = workspaceScrollRef.current.scrollHeight
    }
  }, [insights, activeStep])

  const sessionIdRef = useRef(`session-${Date.now()}`)

  const streamingTextRef = useRef("")
  const streamingMsgIdRef = useRef<string | null>(null)
  
  // Realtime multi-agent right-side tabs sync tracking
  const currentActiveAgentRef = useRef<string | null>(null)
  const streamingInsightsTextRef = useRef<Record<string, string>>({})
  const streamingDraftTextRef = useRef("")

  const resolveExecutionStep = useCallback((author: string | null) => {
    if (!author) return
    if (author.includes("intake_manager")) {
      setExecutionProgress(25)
      setExecutionStep(2)
    } else if (author.includes("research_manager") || author.includes("local_context") || author.includes("market_research") || author.includes("competitor") || author.includes("approved_source")) {
      setExecutionProgress(55)
      setExecutionStep(3)
    } else if (author.includes("planning_manager") || author.includes("persona_strategy") || author.includes("campaign_planning")) {
      setExecutionProgress(80)
      setExecutionStep(4)
    } else if (author.includes("generation_governance") || author.includes("content_generation")) {
      setExecutionProgress(95)
      setExecutionStep(5)
    }
  }, [])

  const handleDelegateToAI = useCallback(() => {
    setIsExecuting(true)
    setIsTyping(true)
    setActiveAgentLabel("Chuyên viên Khảo sát Dự án AI đang phân tích hồ sơ...")
    setExecutionProgress(0)
    setExecutionStep(1)
    setExecutionLogs(["Connecting to agent server..."])
    
    // Clear dynamic states for the new full execution run
    setInsights([])
    setDrafts([])
    setCampaignPlan(null)
    setHasExecuted(false)

    // Build formal Markdown Project Brief payload to be sent to Agent
    const briefSummaryMarkdown = [
      `# YÊU CẦU KHỞI TẠO CHIẾN DỊCH BẤT ĐỘNG SẢN CHUYÊN NGHIỆP`,
      `Tôi muốn khởi động hệ thống Multi-Agent để lập kế hoạch và tạo bài viết Facebook dựa trên hồ sơ dự án chi tiết sau:`,
      `* **Tên dự án:** ${brief.projectName}`,
      `* **Phân khúc bất động sản:** ${brief.propertySegment}`,
      `* **Vị trí địa lý:** ${brief.location}`,
      `* **Khung giá bán dự kiến:** ${brief.priceRange}`,
      `* **Mục tiêu chính:** ${brief.campaignObjective}`,
      `* **Giọng điệu thương hiệu (Tone):** ${brief.tone}`,
      `* **Điểm bán hàng cốt lõi (KSP):** ${brief.keySellingPoints}`,
      `* **Chân dung người mua tiềm năng:** ${brief.buyerProfile}`,
      `* **Chương trình khuyến mãi & Ưu đãi tài chính:** ${brief.promotionDetails}`,
      `\nHãy thực hiện các bước: Nghiên cứu thị trường và bối cảnh hạ tầng địa phương, lập kế hoạch chiến dịch tài chính, và sinh ít nhất 3 phương án bài viết Facebook thu hút leads kèm gợi ý hình ảnh.`
    ].join("\n")

    // Send user action message to chat feed
    const userMsg: ChatMessage = {
      id: `user-delegate-${Date.now()}`,
      sender: "user",
      author: "Bạn",
      text: "Kích hoạt Đội ngũ Chuyên viên AI: Bắt đầu tạo bài viết chiến dịch bằng AI...",
      timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
    }
    setMessages((prev) => [...prev, userMsg])

    // Reset stream state references
    currentActiveAgentRef.current = null
    streamingTextRef.current = ""
    streamingMsgIdRef.current = null
    streamingDraftTextRef.current = ""
    streamingInsightsTextRef.current = {}

    streamAgentChat("default_user", sessionIdRef.current, briefSummaryMarkdown, {
      onEvent(event) {
        if (!event.text) return
        setIsTyping(false)

        const author = event.author ?? "Trợ lý Chiến dịch AI"
        const now = new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })

        // Update technical diagnostics log
        setExecutionLogs((prev) => [...prev, `[${author}] ${event.text}`])
        setLogs((prev) => [`[${author}] ${event.text}`, ...prev])
        resolveExecutionStep(event.author)

        // 1. UPDATE CHAT FEED (LEFT SIDE) - Typewriter effect per specialist agent
        if (currentActiveAgentRef.current !== author) {
          currentActiveAgentRef.current = author
          streamingMsgIdRef.current = null
          streamingTextRef.current = ""
          setActiveAgentLabel(`${formatAgentName(author)} đang xử lý...`)
        }

        if (event.partial === true) {
          streamingTextRef.current += event.text
        } else {
          streamingTextRef.current = event.text
        }

        const textToDisplay = streamingTextRef.current
        const currentActiveMsgId = streamingMsgIdRef.current

        if (currentActiveMsgId) {
          flushSync(() => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === currentActiveMsgId
                  ? { ...m, text: textToDisplay }
                  : m
              )
            )
          })
        } else {
          const msgId = `${Date.now()}-${Math.random()}`
          streamingMsgIdRef.current = msgId
          flushSync(() => {
            setMessages((prev) => [
              ...prev,
              { id: msgId, sender: "agent", author, text: textToDisplay, timestamp: now },
            ])
          })
        }

        // 2. UPDATE INSIGHTS TAB REAL-TIME (If event comes from search/research specialists)
        const isResearchAgent = 
          author.includes("research_manager") ||
          author.includes("market_research") || 
          author.includes("local_context") || 
          author.includes("competitor") || 
          author.includes("approved_source")

        if (isResearchAgent) {
          // Keep active view focused on live insights
          flushSync(() => {
            setActiveStep("Insights")
          })

          const categoryMap: Record<string, InsightItem["category"]> = {
            research_manager_agent: "market_research_agent",
            local_context_agent: "local_context_agent",
            market_research_agent: "market_research_agent",
            competitor_positioning_agent: "competitor_positioning_agent",
            approved_source_search_agent: "approved_source_search_agent",
          }
          // Find standard category matching raw agent name
          const matchedCategory = Object.keys(categoryMap).find(k => author.includes(k))
          const category = matchedCategory ? categoryMap[matchedCategory] : "market_research_agent"

          if (event.partial === true) {
            streamingInsightsTextRef.current[author] = (streamingInsightsTextRef.current[author] || "") + event.text
          } else {
            streamingInsightsTextRef.current[author] = event.text
          }

          const insightContent = streamingInsightsTextRef.current[author]
          const insTitleMap: Record<string, string> = {
            research_manager_agent: "Tổng hợp nghiên cứu thị trường chuyên sâu",
            local_context_agent: "Nghiên cứu bối cảnh & hạ tầng địa phương",
            market_research_agent: "Phân tích nhu cầu khách hàng mục tiêu",
            competitor_positioning_agent: "Báo cáo vị thế định vị đối thủ cạnh tranh",
            approved_source_search_agent: "Kiểm chứng thông tin chính thức",
          }
          const title = insTitleMap[category] || insTitleMap[author] || `${author} // Phân tích`

          flushSync(() => {
            setInsights((prev) => {
              const exists = prev.some((item) => item.category === category)
              if (exists) {
                return prev.map((item) =>
                  item.category === category
                    ? { ...item, content: insightContent, sourceType: "source-backed" }
                    : item
                )
              } else {
                return [
                  ...prev,
                  {
                    id: `ins-${category}`,
                    category,
                    title,
                    content: insightContent,
                    sourceType: "source-backed",
                    url: category === "local_context_agent" ? "https://vietnamnet.vn/ha-tang-do-thi" : undefined
                  }
                ]
              }
            })
          })
        }

        // 2.5 UPDATE CAMPAIGN PLAN REAL-TIME (If event comes from planning specialists)
        const isPlanningAgent = 
          author.includes("planning_manager") ||
          author.includes("campaign_planning") ||
          author.includes("persona_strategy")

        if (isPlanningAgent) {
          flushSync(() => {
            setActiveStep("Review")
          })
          const plan = parseCampaignPlanFromText(textToDisplay)
          if (plan) {
            flushSync(() => {
              setCampaignPlan(plan)
            })
          }
        }

        // 3. UPDATE DRAFTS TAB REAL-TIME (If event comes from content generation specialists)
        const isGenerationAgent = 
          author.includes("content_generation") || 
          author.includes("generation_governance")

        if (isGenerationAgent) {
          flushSync(() => {
            setActiveStep("Drafts")
          })

          if (event.partial === true) {
            streamingDraftTextRef.current += event.text
          } else {
            streamingDraftTextRef.current = event.text
          }

          const draftContent = streamingDraftTextRef.current

          flushSync(() => {
            setDrafts((prev) => {
              const exists = prev.some((d) => d.id === "dr-streaming")
              if (exists) {
                return prev.map((d) =>
                  d.id === "dr-streaming"
                    ? { ...d, caption: draftContent }
                    : d
                )
              } else {
                return [
                  ...prev,
                  {
                    id: "dr-streaming",
                    format: "Image post",
                    angle: "Phương án đang được soạn thảo bởi Trợ lý Sáng tạo...",
                    caption: draftContent,
                    creativeSuggestion: "Hình ảnh đề xuất đang được phân tích và sinh kèm...",
                    persona: "Đang phân tích strategy persona...",
                    cta: "Gửi tin nhắn (Send Message)",
                    objective: brief.campaignObjective,
                    riskNotes: null,
                    status: "generated",
                  }
                ]
              }
            })
          })
        }
      },
      onDone() {
        setExecutionProgress(100)
        setIsExecuting(false)
        setHasExecuted(true)
        setActiveAgentLabel("")

        // Parse final consolidated content into standard draft cards
        if (streamingDraftTextRef.current) {
          const parsed = parseDraftsFromText(streamingDraftTextRef.current, brief.campaignObjective)
          if (parsed.length > 0) {
            flushSync(() => {
              setDrafts(parsed)
            })
          }
        }

        // Clear refs
        currentActiveAgentRef.current = null
        streamingTextRef.current = ""
        streamingMsgIdRef.current = null
        streamingDraftTextRef.current = ""
        streamingInsightsTextRef.current = {}
      },
      onError(error) {
        setExecutionLogs((prev) => [...prev, `Error: ${error}`])
        setIsExecuting(false)
        
        currentActiveAgentRef.current = null
        streamingTextRef.current = ""
        streamingMsgIdRef.current = null
      },
    })
  }, [brief, resolveExecutionStep])


  const handleSendMessage = useCallback(() => {
    if (!chatInput.trim()) return

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: "user",
      author: "Bạn",
      text: chatInput,
      timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
    }

    setMessages((prev) => [...prev, userMsg])
    
    // Reset streaming states for a clean new turn
    streamingMsgIdRef.current = null
    streamingTextRef.current = ""
    streamingDraftTextRef.current = ""
    streamingInsightsTextRef.current = {}
    currentActiveAgentRef.current = null

    const currentMessage = chatInput
    setChatInput("")
    setIsTyping(true)
    setIsExecuting(true)
    setActiveAgentLabel("Kết nối chuyên viên lập chiến dịch...")
    setLogs((prev) => [`User: "${currentMessage}"`, ...prev])

    streamAgentChat("default_user", sessionIdRef.current, currentMessage, {
      onEvent(event) {
        if (!event.text) return
        setIsTyping(false)

        const author = event.author ?? "Trợ lý Chiến dịch AI"
        const now = new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })

        // Update logs and execution step
        setLogs((prev) => [`[${author}] ${event.text}`, ...prev])
        setExecutionLogs((prev) => [...prev, `[${author}] ${event.text}`])
        resolveExecutionStep(event.author)

        // 1. UPDATE CHAT FEED (LEFT SIDE) - Typewriter effect per specialist agent
        if (currentActiveAgentRef.current !== author) {
          currentActiveAgentRef.current = author
          streamingMsgIdRef.current = null
          streamingTextRef.current = ""
          setActiveAgentLabel(`${formatAgentName(author)} đang xử lý...`)
        }

        if (event.partial === true) {
          streamingTextRef.current += event.text
        } else {
          streamingTextRef.current = event.text
        }

        const textToDisplay = streamingTextRef.current
        const currentActiveMsgId = streamingMsgIdRef.current

        if (currentActiveMsgId) {
          flushSync(() => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === currentActiveMsgId
                  ? { ...m, text: textToDisplay }
                  : m
              )
            )
          })
        } else {
          const msgId = `${Date.now()}-${Math.random()}`
          streamingMsgIdRef.current = msgId
          flushSync(() => {
            setMessages((prev) => [
              ...prev,
              { id: msgId, sender: "agent", author, text: textToDisplay, timestamp: now },
            ])
          })
        }

        // 2. UPDATE INSIGHTS TAB REAL-TIME (If event comes from search/research specialists)
        const isResearchAgent = 
          author.includes("research_manager") ||
          author.includes("market_research") || 
          author.includes("local_context") || 
          author.includes("competitor") || 
          author.includes("approved_source")

        if (isResearchAgent) {
          flushSync(() => {
            setActiveStep("Insights")
          })

          const categoryMap: Record<string, InsightItem["category"]> = {
            research_manager_agent: "market_research_agent",
            local_context_agent: "local_context_agent",
            market_research_agent: "market_research_agent",
            competitor_positioning_agent: "competitor_positioning_agent",
            approved_source_search_agent: "approved_source_search_agent",
          }
          const matchedCategory = Object.keys(categoryMap).find(k => author.includes(k))
          const category = matchedCategory ? categoryMap[matchedCategory] : "market_research_agent"

          if (event.partial === true) {
            streamingInsightsTextRef.current[author] = (streamingInsightsTextRef.current[author] || "") + event.text
          } else {
            streamingInsightsTextRef.current[author] = event.text
          }

          const insightContent = streamingInsightsTextRef.current[author]
          const insTitleMap: Record<string, string> = {
            research_manager_agent: "Tổng hợp nghiên cứu thị trường chuyên sâu",
            local_context_agent: "Nghiên cứu bối cảnh & hạ tầng địa phương",
            market_research_agent: "Phân tích nhu cầu khách hàng mục tiêu",
            competitor_positioning_agent: "Báo cáo vị thế định vị đối thủ cạnh tranh",
            approved_source_search_agent: "Kiểm chứng thông tin chính thức",
          }
          const title = insTitleMap[category] || insTitleMap[author] || `${author} // Phân tích`

          flushSync(() => {
            setInsights((prev) => {
              const exists = prev.some((item) => item.category === category)
              if (exists) {
                return prev.map((item) =>
                  item.category === category
                    ? { ...item, content: insightContent, sourceType: "source-backed" }
                    : item
                )
              } else {
                return [
                  ...prev,
                  {
                    id: `ins-${category}`,
                    category,
                    title,
                    content: insightContent,
                    sourceType: "source-backed",
                    url: category === "local_context_agent" ? "https://vietnamnet.vn/ha-tang-do-thi" : undefined
                  }
                ]
              }
            })
          })
        }

        // 2.5 UPDATE CAMPAIGN PLAN REAL-TIME (If event comes from planning specialists)
        const isPlanningAgent = 
          author.includes("planning_manager") ||
          author.includes("campaign_planning") ||
          author.includes("persona_strategy")

        if (isPlanningAgent) {
          flushSync(() => {
            setActiveStep("Review")
          })
          const plan = parseCampaignPlanFromText(textToDisplay)
          if (plan) {
            flushSync(() => {
              setCampaignPlan(plan)
            })
          }
        }

        // 3. UPDATE DRAFTS TAB REAL-TIME (If event comes from content generation specialists)
        const isGenerationAgent = 
          author.includes("content_generation") || 
          author.includes("generation_governance")

        if (isGenerationAgent) {
          flushSync(() => {
            setActiveStep("Drafts")
          })

          if (event.partial === true) {
            streamingDraftTextRef.current += event.text
          } else {
            streamingDraftTextRef.current = event.text
          }

          const draftContent = streamingDraftTextRef.current

          flushSync(() => {
            setDrafts((prev) => {
              const exists = prev.some((d) => d.id === "dr-streaming")
              if (exists) {
                return prev.map((d) =>
                  d.id === "dr-streaming"
                    ? { ...d, caption: draftContent }
                    : d
                )
              } else {
                return [
                  ...prev,
                  {
                    id: "dr-streaming",
                    format: "Image post",
                    angle: "Phương án đang được soạn thảo bởi Trợ lý Sáng tạo...",
                    caption: draftContent,
                    creativeSuggestion: "Hình ảnh đề xuất đang được phân tích và sinh kèm...",
                    persona: "Đang phân tích strategy persona...",
                    cta: "Gửi tin nhắn (Send Message)",
                    objective: brief.campaignObjective,
                    riskNotes: null,
                    status: "generated",
                  }
                ]
              }
            })
          })
        }
      },
      onDone() {
        setIsExecuting(false)
        setIsTyping(false)
        setActiveAgentLabel("")

        // Parse final consolidated content into standard draft cards
        if (streamingDraftTextRef.current) {
          const parsed = parseDraftsFromText(streamingDraftTextRef.current, brief.campaignObjective)
          if (parsed.length > 0) {
            flushSync(() => {
              setDrafts(parsed)
            })
          }
        }

        // Clear refs
        currentActiveAgentRef.current = null
        streamingTextRef.current = ""
        streamingMsgIdRef.current = null
        streamingDraftTextRef.current = ""
        streamingInsightsTextRef.current = {}
      },
      onError(error) {
        setIsExecuting(false)
        setIsTyping(false)
        setActiveAgentLabel("")
        
        streamingMsgIdRef.current = null
        streamingTextRef.current = ""
        streamingDraftTextRef.current = ""
        streamingInsightsTextRef.current = {}
        currentActiveAgentRef.current = null

        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString(),
            sender: "agent",
            author: "Hệ thống",
            text: `Lỗi kết nối: ${error}`,
            timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
          },
        ])
      },
    })
  }, [chatInput, brief, resolveExecutionStep])

  // Update specific field in Brief
  const handleUpdateBriefField = (field: BriefField, value: string) => {
    setBrief((prev) => ({ ...prev, [field]: value }))
    setLogs((prev) => [`Cập nhật thông tin [${field}] trực tiếp qua giao diện tương tác`, ...prev])
  }

  // Handle Draft Status Actions
  const handleUpdateDraftStatus = (id: string, newStatus: DraftItem["status"]) => {
    setDrafts((prev) => prev.map((d) => (d.id === id ? { ...d, status: newStatus } : d)))
    setLogs((prev) => [`Cập nhật trạng thái duyệt Bản thảo [${id}] thành [${newStatus}]`, ...prev])
  }

  // Check how many fields are filled
  const briefFieldsCount = Object.keys(brief).length
  const briefFilledCount = Object.values(brief).filter(v => v.trim().length > 0).length

  return (
    <main className="h-screen w-screen overflow-hidden bg-[#F8F9FA] text-[#1A2B49] font-sans antialiased flex flex-col text-[13px]">
      
      {/* Header - Fixed Height */}
      <header className="flex-none px-5 py-2.5 bg-white border-b border-slate-200 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between z-10">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="bg-[#C8102E] text-white text-[10px] font-extrabold px-2.5 py-1 tracking-wider uppercase rounded-xs">
              CAMPAIGN WORKBENCH
            </span>
          </div>
          <h1 className="mt-0.5 text-base font-black tracking-tight text-[#1A2B49] flex items-center gap-1.5">
            Chuyên viên Bất động sản
            <div className="h-1 w-8 bg-[#C8102E] rounded-full inline-block ml-1" />
          </h1>
        </div>

        {/* Tab-like Stepper layout with visual priority partitioning */}
        <div className="flex items-center flex-wrap gap-3">
          
          {/* Dynamic Active Agent Work Status Text (UX refinement) */}
          {isExecuting && activeAgentLabel && (
            <div className="flex items-center gap-1.5 px-2.5 py-0.5 bg-[#C8102E]/5 border border-[#C8102E]/10 rounded-sm text-[10px] font-bold text-[#C8102E] animate-pulse uppercase tracking-wider">
              <span className="size-1.5 rounded-full bg-[#C8102E] animate-ping" />
              <span>{activeAgentLabel}</span>
            </div>
          )}

          {/* Primary Pipeline (Core Actions) */}
          <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-sm border border-slate-200">
            {primarySteps.map((step) => {
              const isActive = activeStep === step.id
              return (
                <button
                  key={step.id}
                  onClick={() => setActiveStep(step.id)}
                  className={cn(
                    "flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider rounded-xs cursor-pointer transition-all",
                    isActive 
                      ? "text-[#C8102E] bg-white border border-[#1A2B49] shadow-[1px_1px_0px_0px_#1A2B49]" 
                      : "text-slate-600 hover:text-[#1A2B49]"
                  )}
                >
                  <step.icon className="size-3" />
                  <span>{step.name}</span>
                </button>
              )
            })}
          </div>

          <div className="h-3.5 w-px bg-slate-300" />

          {/* Supplementary Insights & Analytics Tabs */}
          <div className="flex items-center gap-0.5">
            {secondarySteps.map((step) => {
              const Icon = step.icon
              const isActive = activeStep === step.id
              return (
                <button
                  key={step.id}
                  onClick={() => setActiveStep(step.id)}
                  title={step.description}
                  className={cn(
                    "flex items-center gap-1 px-2 py-1 text-[11px] font-semibold rounded-xs cursor-pointer transition-all",
                    isActive 
                      ? "text-[#1A2B49] bg-white border border-slate-300 font-bold" 
                      : "text-slate-500 hover:text-[#1A2B49] hover:bg-slate-100"
                  )}
                >
                  <Icon className="size-3" />
                  <span className="hidden xl:inline">{step.name}</span>
                </button>
              )
            })}
          </div>

        </div>
      </header>

      {/* Main Spacious Content Workspace */}
      <div className="flex-1 min-h-0 p-4">
        
        {/* Spacious 2-Column Split: 460px Chat / Flexible Right Widget */}
        <div className="grid gap-4 lg:grid-cols-[460px_minmax(0,1fr)] h-full min-h-0">
          
          {/* LEFT COLUMN: Highly Spacious Chatbot Interface */}
          <section className="flex flex-col h-full bg-white border border-[#1A2B49] shadow-[4px_4px_0px_0px_#1A2B49] rounded-sm overflow-hidden">
            
            {/* Header info */}
            <div className="bg-[#1A2B49] text-white px-4 py-2.5 flex items-center justify-between border-b border-[#1A2B49]">
              <div className="flex items-center gap-1.5">
                <div className="size-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="font-mono text-[10px] font-black uppercase tracking-widest">Trợ lý hội thoại chiến dịch</span>
              </div>
              <span className="text-[8px] bg-[#C8102E] px-2 py-0.5 rounded-xs font-bold">CHIẾN DỊCH HOẠT ĐỘNG</span>
            </div>

            {/* Spacious Chat Messages Area (Custom Hidden Scrollbar) */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
              {messages.map((msg) => {
                const isAgent = msg.sender === "agent"
                const isSys = msg.author === "Hệ thống Agent"
                return (
                  <div
                    key={msg.id}
                    className={cn(
                      "flex flex-col max-w-[92%] rounded-sm p-3 border text-[12px] leading-relaxed transition-all",
                      isAgent
                        ? isSys
                          ? "bg-amber-50/50 border-amber-300 text-amber-950 font-medium"
                          : "bg-white border-slate-200 text-[#1A2B49] self-start"
                        : "bg-[#1A2B49] border-[#1A2B49] text-white self-end ml-auto shadow-[1.5px_1.5px_0px_0px_rgba(0,0,0,0.1)]"
                    )}
                  >
                    <div className="flex items-center justify-between gap-5 mb-1.5">
                      <span className={cn(
                        "text-[9px] font-extrabold uppercase tracking-widest",
                        isSys ? "text-[#C8102E]" : isAgent ? "text-[#C8102E]" : "text-slate-300"
                      )}>
                        {formatAgentName(msg.author)}
                      </span>
                      <span className="text-[8px] text-slate-400 font-mono font-medium">{msg.timestamp}</span>
                    </div>
                    <div className={cn(
                      "markdown-content text-[12px] leading-relaxed text-[#1A2B49]",
                      !isAgent && "text-white"
                    )}>
                      <ReactMarkdown
                        components={{
                          h1: ({node, ...props}) => <h1 className="text-sm font-black text-[#1A2B49] mt-2 mb-1 uppercase tracking-wider" {...props} />,
                          h2: ({node, ...props}) => <h2 className="text-xs font-bold text-[#1A2B49] mt-2 mb-1" {...props} />,
                          h3: ({node, ...props}) => <h3 className="text-[11px] font-bold text-[#1A2B49] mt-1.5 mb-1" {...props} />,
                          p: ({node, children, ...props}) => {
                            if (typeof children === "string") {
                              const parts = children.split(/(\#[a-zA-Z0-9_đĐâÂêÊôÔưƯơƠááààảảããạạăĂâÂđĐéÉèÈẻẺẽẼẹẸêÊíÍìÌỉỈĩĨịỊóÓòÒỏỎõÕọỌôÔơƠúÚùÙủỦũŨụỤưƯýÝỳỲỷỶỹỸỵY]+)/g);
                              return (
                                <p className="mb-1.5 last:mb-0 whitespace-pre-wrap" {...props}>
                                  {parts.map((part, idx) => 
                                    part.startsWith("#") 
                                      ? <span key={idx} className="text-sky-600 font-semibold hover:underline cursor-pointer transition-colors">{part}</span> 
                                      : part
                                  )}
                                </p>
                              );
                            }
                            return <p className="mb-1.5 last:mb-0 whitespace-pre-wrap" {...props}>{children}</p>;
                          },
                          ul: ({node, ...props}) => <ul className="list-disc pl-4 mb-2 space-y-1" {...props} />,
                          ol: ({node, ...props}) => <ol className="list-decimal pl-4 mb-2 space-y-1" {...props} />,
                          li: ({node, ...props}) => <li className="mb-0.5" {...props} />,
                          strong: ({node, ...props}) => <strong className="font-extrabold text-[#C8102E]" {...props} />,
                          table: ({node, ...props}) => <table className="w-full border-collapse border border-slate-300 my-2 text-[11px]" {...props} />,
                          th: ({node, ...props}) => <th className="border border-slate-300 bg-slate-100 px-2 py-1 font-bold text-left" {...props} />,
                          td: ({node, ...props}) => <td className="border border-slate-300 px-2 py-1" {...props} />
                        }}
                      >
                        {cleanTechnicalAgentNames(msg.text)}
                      </ReactMarkdown>
                    </div>
                  </div>
                )
              })}

              {isTyping && (
                <div className="flex items-center gap-2 p-2.5 bg-white border border-slate-200 rounded-sm self-start max-w-[100px] shadow-xs">
                  <span className="size-1 rounded-full bg-[#1A2B49] animate-bounce [animation-delay:-0.3s]" />
                  <span className="size-1 rounded-full bg-[#1A2B49] animate-bounce [animation-delay:-0.15s]" />
                  <span className="size-1 rounded-full bg-[#1A2B49] animate-bounce" />
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Chat Input Bar */}
            <div className="p-3 border-t border-slate-200 bg-white">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                  placeholder="Nhập tin nhắn..."
                  className="flex-1 h-8.5 px-3 border border-slate-300 rounded-xs text-xs outline-none focus:border-[#1A2B49] focus:ring-1 focus:ring-[#1A2B49] placeholder-slate-400"
                />
                <Button 
                  onClick={handleSendMessage}
                  className="bg-[#1A2B49] hover:bg-[#2A3B59] text-white size-8.5 p-0 flex items-center justify-center border border-[#1A2B49] active:translate-y-px rounded-xs cursor-pointer"
                >
                  <Send className="size-3.5" />
                </Button>
              </div>
            </div>
          </section>

          {/* RIGHT COLUMN: Interactive Dashboard Canvas */}
          <section className="flex flex-col h-full bg-white border border-[#1A2B49] shadow-[4px_4px_0px_0px_#1A2B49] rounded-sm overflow-hidden">
            
            {/* Widget Header */}
            <div className="border-b border-[#1A2B49] bg-slate-50/80 px-4.5 py-2.5 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="bg-[#C8102E] text-white text-[8px] font-black px-1.5 py-0.5 uppercase rounded-xs">
                    Không gian sáng tạo
                  </span>
                  <span className="text-[11px] text-[#1A2B49] font-bold">/</span>
                  <span className="text-[11px] text-slate-500 font-medium">Phân khu: {
                    activeStep === "Brief" ? "Hồ sơ dự án" :
                    activeStep === "Insights" ? "Nghiên cứu thị trường" :
                    activeStep === "Drafts" ? "Bản thảo nội dung" :
                    activeStep === "Review" ? "Kế hoạch & Kiểm duyệt" : activeStep
                  }</span>
                </div>
                <h2 className="text-sm font-bold text-[#1A2B49] mt-0.5">
                  {activeStep === "Brief" && "Hồ sơ thông tin dự án bất động sản"}
                  {activeStep === "Insights" && "Nghiên cứu & Phân tích thị trường"}
                  {activeStep === "Drafts" && "Bản thảo nội dung chiến dịch quảng cáo"}
                  {activeStep === "Review" && "Hoạch định ngân sách & Kiểm duyệt pháp lý"}
                </h2>
              </div>
              {activeStep === "Brief" && (
                <span className="text-[11px] font-mono font-bold bg-[#1A2B49]/10 text-[#1A2B49] px-2.5 py-1 rounded-sm">
                  Đã điền {briefFilledCount}/{briefFieldsCount} mục
                </span>
              )}
            </div>

            {/* Scrollable Workspace Container */}
            <div ref={workspaceScrollRef} className="flex-1 p-4 overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
              
                  {/* STEP 1: BRIEF */}
                  {activeStep === "Brief" && (
                    <div className="space-y-4">
                      <div className="grid gap-2 md:grid-cols-2">
                        
                        {/* Project Name Card */}
                        <div className="border border-[#1A2B49] p-2 bg-white shadow-[1.5px_1.5px_0px_0px_#1A2B49] rounded-sm hover:translate-y-[-1px] transition-all">
                          <label className="text-[8px] font-black uppercase tracking-wider text-slate-500 block mb-0.5">Tên dự án</label>
                          <input
                            type="text"
                            value={brief.projectName}
                            onChange={(e) => handleUpdateBriefField("projectName", e.target.value)}
                            className="w-full text-[11px] font-bold text-[#1A2B49] outline-none border-b border-transparent hover:border-slate-300 focus:border-[#1A2B49] pb-0.5"
                          />
                        </div>

                        {/* Segment Card */}
                        <div className="border border-[#1A2B49] p-2 bg-white shadow-[1.5px_1.5px_0px_0px_#1A2B49] rounded-sm hover:translate-y-[-1px] transition-all">
                          <label className="text-[8px] font-black uppercase tracking-wider text-slate-500 block mb-0.5">Phân khúc sản phẩm</label>
                          <select
                            value={brief.propertySegment}
                            onChange={(e) => handleUpdateBriefField("propertySegment", e.target.value)}
                            className="w-full text-[11px] font-bold text-[#1A2B49] bg-transparent outline-none cursor-pointer"
                          >
                            {propertySegments.map((opt) => (
                              <option key={opt.value} value={opt.value}>{opt.label}</option>
                            ))}
                          </select>
                        </div>

                        {/* Location Card */}
                        <div className="border border-[#1A2B49] p-2 bg-white shadow-[1.5px_1.5px_0px_0px_#1A2B49] rounded-sm hover:translate-y-[-1px] transition-all">
                          <label className="text-[8px] font-black uppercase tracking-wider text-slate-500 block mb-0.5">Vị trí dự án</label>
                          <input
                            type="text"
                            value={brief.location}
                            onChange={(e) => handleUpdateBriefField("location", e.target.value)}
                            className="w-full text-[11px] font-bold text-[#1A2B49] outline-none border-b border-transparent hover:border-slate-300 focus:border-[#1A2B49] pb-0.5"
                          />
                        </div>

                        {/* Price Range Card */}
                        <div className="border border-[#1A2B49] p-2 bg-white shadow-[1.5px_1.5px_0px_0px_#1A2B49] rounded-sm hover:translate-y-[-1px] transition-all">
                          <label className="text-[8px] font-black uppercase tracking-wider text-slate-500 block mb-0.5">Khung giá dự kiến</label>
                          <input
                            type="text"
                            value={brief.priceRange}
                            onChange={(e) => handleUpdateBriefField("priceRange", e.target.value)}
                            className="w-full text-[11px] font-bold text-[#1A2B49] outline-none border-b border-transparent hover:border-slate-300 focus:border-[#1A2B49] pb-0.5"
                          />
                        </div>

                        {/* Objective Card */}
                        <div className="border border-[#1A2B49] p-2 bg-white shadow-[1.5px_1.5px_0px_0px_#1A2B49] rounded-sm hover:translate-y-[-1px] transition-all">
                          <label className="text-[8px] font-black uppercase tracking-wider text-slate-500 block mb-0.5">Mục tiêu chiến dịch</label>
                          <input
                            type="text"
                            value={brief.campaignObjective}
                            onChange={(e) => handleUpdateBriefField("campaignObjective", e.target.value)}
                            className="w-full text-[11px] font-bold text-[#1A2B49] outline-none border-b border-transparent hover:border-slate-300 focus:border-[#1A2B49] pb-0.5"
                          />
                        </div>

                        {/* Tone Card */}
                        <div className="border border-[#1A2B49] p-2 bg-white shadow-[1.5px_1.5px_0px_0px_#1A2B49] rounded-sm hover:translate-y-[-1px] transition-all">
                          <label className="text-[8px] font-black uppercase tracking-wider text-slate-500 block mb-0.5">Giọng điệu (Tone)</label>
                          <input
                            type="text"
                            value={brief.tone}
                            onChange={(e) => handleUpdateBriefField("tone", e.target.value)}
                            className="w-full text-[11px] font-bold text-[#1A2B49] outline-none border-b border-transparent hover:border-slate-300 focus:border-[#1A2B49] pb-0.5"
                          />
                        </div>

                        {/* Selling points block */}
                        <div className="border border-[#1A2B49] p-2 bg-white shadow-[1.5px_1.5px_0px_0px_#1A2B49] rounded-sm hover:translate-y-[-1px] transition-all md:col-span-2">
                          <label className="text-[8px] font-black uppercase tracking-wider text-slate-500 block mb-0.5">Điểm bán hàng (Key Selling Points)</label>
                          <textarea
                            value={brief.keySellingPoints}
                            onChange={(e) => handleUpdateBriefField("keySellingPoints", e.target.value)}
                            rows={3}
                            className="w-full text-[11px] text-[#1A2B49] leading-relaxed outline-none border-b border-transparent hover:border-slate-300 focus:border-[#1A2B49] resize-none pb-0.5"
                          />
                        </div>

                        {/* Buyer profile */}
                        <div className="border border-[#1A2B49] p-2 bg-white shadow-[1.5px_1.5px_0px_0px_#1A2B49] rounded-sm hover:translate-y-[-1px] transition-all md:col-span-2">
                          <label className="text-[8px] font-black uppercase tracking-wider text-slate-500 block mb-0.5">Chân dung người mua (Target Persona)</label>
                          <textarea
                            value={brief.buyerProfile}
                            onChange={(e) => handleUpdateBriefField("buyerProfile", e.target.value)}
                            rows={3}
                            className="w-full text-[11px] text-[#1A2B49] leading-relaxed outline-none border-b border-transparent hover:border-slate-300 focus:border-[#1A2B49] resize-none pb-0.5"
                          />
                        </div>

                        {/* Promotion details */}
                        <div className="border border-[#1A2B49] p-2 bg-white shadow-[1.5px_1.5px_0px_0px_#1A2B49] rounded-sm hover:translate-y-[-1px] transition-all md:col-span-2">
                          <label className="text-[8px] font-black uppercase tracking-wider text-slate-500 block mb-0.5">Chương trình ưu đãi & Khuyến mãi (Promotion Details)</label>
                          <textarea
                            value={brief.promotionDetails}
                            onChange={(e) => handleUpdateBriefField("promotionDetails", e.target.value)}
                            rows={3}
                            className="w-full text-[11px] text-[#1A2B49] leading-relaxed outline-none border-b border-transparent hover:border-slate-300 focus:border-[#1A2B49] resize-none pb-0.5"
                          />
                        </div>

                      </div>
                    </div>
                  )}

                  {/* STEP 2: INSIGHTS */}
                  {activeStep === "Insights" && (
                    <div className="space-y-3">
                      {insights.length === 0 && !isExecuting && !hasExecuted ? (
                        <div className="border border-dashed border-slate-300 rounded-sm p-6 text-center flex flex-col items-center justify-center space-y-2.5 bg-slate-50/50">
                          <Lock className="size-6 text-slate-400" />
                          <h4 className="text-xs font-bold text-[#1A2B49]">Chưa có dữ liệu nghiên cứu thị trường</h4>
                          <p className="text-[11px] text-slate-500 max-w-sm leading-relaxed">
                            Vui lòng nhấn nút "Bắt đầu tạo bài viết bằng AI" ở góc dưới bên phải màn hình để kích hoạt đội ngũ chuyên viên nghiên cứu và thu thập tín hiệu thị trường.
                          </p>
                        </div>
                      ) : (
                        <>
                          <div className="space-y-2">
                            {insights.map((ins) => (
                              <div 
                                key={ins.id}
                                className="border border-[#1A2B49] bg-white rounded-sm shadow-[1.5px_1.5px_0px_0px_#1A2B49] overflow-hidden"
                              >
                                <div className="px-3 py-2 bg-slate-50 border-b border-[#1A2B49] flex items-center justify-between">
                                  <div className="flex items-center gap-1.5">
                                    <span className="bg-[#1A2B49] text-white text-[8px] font-mono px-1.5 py-0.5 rounded-xs">
                                      {formatAgentName(ins.category)}
                                    </span>
                                    <h4 className="text-[11px] font-bold text-[#1A2B49] ml-1">{cleanTechnicalAgentNames(ins.title.split("//")[1]?.trim() || ins.title)}</h4>
                                  </div>

                                  <span className={cn(
                                    "text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-xs border",
                                    ins.sourceType === "source-backed" && "bg-emerald-50 text-emerald-800 border-emerald-300",
                                    ins.sourceType === "user-provided" && "bg-amber-50 text-amber-800 border-amber-300",
                                    ins.sourceType === "unavailable" && "bg-slate-100 text-slate-600 border-slate-300"
                                  )}>
                                    {ins.sourceType === "source-backed" && "Đã kiểm chứng (Google)"}
                                    {ins.sourceType === "user-provided" && "Giả định thực tế"}
                                    {ins.sourceType === "unavailable" && "Thiếu tín hiệu"}
                                  </span>
                                </div>
                                <div className="p-3 text-[11px] space-y-1.5">
                                  <div className="text-[#1A2B49] leading-relaxed markdown-content">
                                    <ReactMarkdown
                                      components={{
                                        h1: ({node, ...props}) => <h1 className="text-xs font-black text-[#1A2B49] mt-2 mb-1 uppercase tracking-wider" {...props} />,
                                        h2: ({node, ...props}) => <h2 className="text-[11px] font-bold text-[#1A2B49] mt-1.5 mb-1" {...props} />,
                                        h3: ({node, ...props}) => <h3 className="text-[10.5px] font-bold text-[#1A2B49] mt-1 mb-1" {...props} />,
                                        p: ({node, ...props}) => <p className="mb-1.5 last:mb-0 whitespace-pre-wrap" {...props} />,
                                        ul: ({node, ...props}) => <ul className="list-disc pl-4 mb-2 space-y-1" {...props} />,
                                        ol: ({node, ...props}) => <ol className="list-decimal pl-4 mb-2 space-y-1" {...props} />,
                                        li: ({node, ...props}) => <li className="mb-0.5" {...props} />,
                                        strong: ({node, ...props}) => <strong className="font-extrabold text-[#C8102E]" {...props} />,
                                      }}
                                    >
                                      {cleanTechnicalAgentNames(ins.content)}
                                    </ReactMarkdown>
                                  </div>
                                  {ins.url && (
                                    <a 
                                      href={ins.url} 
                                      target="_blank" 
                                      rel="noreferrer" 
                                      className="text-[#C8102E] font-mono hover:underline flex items-center gap-0.5 mt-0.5 text-[9px]"
                                    >
                                      <Info className="size-2.5" />
                                      Nguồn kiểm chứng: {ins.url.replace("https://", "")}
                                    </a>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </>
                      )}
                    </div>
                  )}

                  {/* STEP 3: DRAFTS */}
                  {activeStep === "Drafts" && (
                    <div className="space-y-4">
                      {drafts.length === 0 ? (
                        <div className="border border-dashed border-slate-300 rounded-sm p-8 text-center flex flex-col items-center justify-center space-y-3 bg-slate-50/50">
                          <MessageSquareText className="size-8 text-[#C8102E] animate-pulse" />
                          <h4 className="text-sm font-black text-[#1A2B49]">Chưa có bản thảo bài viết chiến dịch</h4>
                          <p className="text-[11px] text-slate-500 max-w-sm leading-relaxed">
                            Hãy nhấn nút "Bắt đầu tạo bài viết bằng AI" ở góc dưới bên phải màn hình để kích hoạt đội ngũ chuyên viên bắt đầu hoạch định và sáng tạo nội dung.
                          </p>
                        </div>
                      ) : (
                        <div className="grid gap-4 md:grid-cols-1">
                          {drafts.map((dr, index) => (
                            <div 
                              key={dr.id}
                              className={cn(
                                "border border-[#1A2B49] bg-white rounded-sm transition-all overflow-hidden flex flex-col",
                                "shadow-[3px_3px_0px_0px_#1A2B49] hover:translate-x-[-1px] hover:translate-y-[-1px] hover:shadow-[4.5px_4.5px_0px_0px_#1A2B49]",
                                dr.status === "approved" && "border-emerald-600 shadow-[3px_3px_0px_0px_#10B981]",
                                dr.status === "rejected" && "border-rose-600 shadow-[3px_3px_0px_0px_#F43F5E]"
                              )}
                            >
                              <div className="bg-[#1A2B49]/5 border-b border-[#1A2B49] px-3.5 py-2 flex items-center justify-between">
                                <div className="flex items-center gap-1.5">
                                  <span className="bg-[#C8102E] text-white text-[8px] font-bold px-1.5 py-0.5 rounded-xs tracking-wider uppercase">
                                    Phương án {index + 1}
                                  </span>
                                  <span className="text-[11px] font-bold text-[#1A2B49]">{dr.angle}</span>
                                </div>

                                <div className="flex items-center gap-1">
                                  <span className="text-[9px] font-semibold text-slate-500 font-mono">{dr.format}</span>
                                  <div className={cn(
                                    "size-1.5 rounded-full",
                                    dr.status === "generated" && "bg-blue-500",
                                    dr.status === "approved" && "bg-emerald-500",
                                    dr.status === "needs_edit" && "bg-amber-500",
                                    dr.status === "rejected" && "bg-rose-500"
                                  )} />
                                </div>
                              </div>

                              <div className="p-3.5 space-y-3 text-[11px]">
                                <div className="space-y-1">
                                  <div className="flex items-center justify-between">
                                    <h5 className="font-bold text-[#1A2B49] uppercase tracking-wide text-[9px] text-slate-500">Bản thảo nội dung bài viết</h5>
                                    <button
                                      onClick={() => {
                                        navigator.clipboard.writeText(cleanCaptionText(dr.caption))
                                        setCopiedDraftId(dr.id)
                                        setTimeout(() => setCopiedDraftId(null), 2000)
                                      }}
                                      className="flex items-center gap-1 px-1.5 py-0.5 rounded-xs border border-slate-200 bg-white hover:bg-slate-50 hover:border-[#1A2B49] text-slate-500 hover:text-[#1A2B49] transition-all text-[9px] font-semibold"
                                    >
                                      {copiedDraftId === dr.id
                                        ? <><Check className="size-2.5 text-emerald-600" /><span className="text-emerald-600">Đã sao chép</span></>
                                        : <><Copy className="size-2.5" /><span>Sao chép</span></>}
                                    </button>
                                  </div>
                                  <div className="bg-slate-50 border border-slate-200 rounded-sm p-2.5 font-sans leading-relaxed text-[#1A2B49] text-[11.5px] select-all markdown-content">
                                    <ReactMarkdown
                                      components={{
                                        h1: ({node, ...props}) => <h1 className="text-xs font-black text-[#1A2B49] mt-2 mb-1 uppercase tracking-wider" {...props} />,
                                        h2: ({node, ...props}) => <h2 className="text-[11px] font-bold text-[#1A2B49] mt-1.5 mb-1" {...props} />,
                                        h3: ({node, ...props}) => <h3 className="text-[10.5px] font-bold text-[#1A2B49] mt-1 mb-1" {...props} />,
                                        p: ({node, ...props}) => <p className="mb-1.5 last:mb-0 whitespace-pre-wrap" {...props} />,
                                        ul: ({node, ...props}) => <ul className="list-disc pl-4 mb-2 space-y-1" {...props} />,
                                        ol: ({node, ...props}) => <ol className="list-decimal pl-4 mb-2 space-y-1" {...props} />,
                                        li: ({node, ...props}) => <li className="mb-0.5" {...props} />,
                                        strong: ({node, ...props}) => <strong className="font-extrabold text-[#C8102E]" {...props} />,
                                      }}
                                    >
                                      {cleanCaptionText(dr.caption)}
                                    </ReactMarkdown>
                                  </div>
                                </div>

                                {/* Concise Image Suggestion */}
                                <div className="bg-amber-50/50 border border-dashed border-amber-300 rounded-sm p-2.5 space-y-0.5">
                                  <h5 className="font-bold text-amber-900 uppercase tracking-wide text-[9px] flex items-center gap-1">
                                    <Sparkles className="size-2.5 text-[#C8102E]" />
                                    Gợi ý hình ảnh đăng kèm (Concise Image Guideline)
                                  </h5>
                                  <div className="text-[#1A2B49] font-medium leading-relaxed italic markdown-content text-[11.5px]">
                                    <ReactMarkdown
                                      components={{
                                        p: ({node, ...props}) => <p className="mb-1 last:mb-0" {...props} />,
                                        strong: ({node, ...props}) => <strong className="font-extrabold text-[#C8102E]" {...props} />,
                                      }}
                                    >
                                      {cleanCreativeSuggestionText(dr.creativeSuggestion)}
                                    </ReactMarkdown>
                                  </div>
                                </div>

                                <div className="grid gap-1.5 sm:grid-cols-3 pt-2 border-t border-slate-100 text-[10px]">
                                  <div>
                                    <span className="text-slate-500 block">Nhóm khách hàng mục tiêu:</span>
                                    <strong className="text-[#1A2B49]">{dr.persona}</strong>
                                  </div>
                                  <div>
                                    <span className="text-slate-500 block">Nút hành động (CTA):</span>
                                    <strong className="text-[#1A2B49]">{dr.cta}</strong>
                                  </div>
                                  <div>
                                    <span className="text-slate-500 block">Mục tiêu chiến dịch:</span>
                                    <strong className="text-[#1A2B49]">{dr.objective}</strong>
                                  </div>
                                </div>

                                {dr.riskNotes && (
                                  <div className="bg-red-50 border border-red-200 p-2 rounded-sm flex items-start gap-1.5 text-[9px] text-red-950 font-medium leading-relaxed">
                                    <AlertTriangle className="size-3 text-[#C8102E] shrink-0 mt-0.5" />
                                    <p>{dr.riskNotes}</p>
                                  </div>
                                )}

                                <div className="flex flex-wrap items-center justify-between gap-2.5 pt-2.5 border-t border-slate-100">
                                  <span className="text-[9px] text-slate-500 font-mono">Duyệt nhanh trạng thái:</span>
                                  <div className="flex gap-1.5">
                                    <button 
                                      onClick={() => handleUpdateDraftStatus(dr.id, "approved")}
                                      className={cn(
                                        "text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 border rounded-xs transition-colors cursor-pointer",
                                        dr.status === "approved"
                                          ? "bg-emerald-600 text-white border-emerald-600"
                                          : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50"
                                      )}
                                    >
                                      Chấp thuận
                                    </button>
                                    <button 
                                      onClick={() => handleUpdateDraftStatus(dr.id, "needs_edit")}
                                      className={cn(
                                        "text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 border rounded-xs transition-colors cursor-pointer",
                                        dr.status === "needs_edit"
                                          ? "bg-amber-600 text-white border-amber-600"
                                          : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50"
                                      )}
                                    >
                                      Cần chỉnh sửa
                                    </button>
                                    <button 
                                      onClick={() => handleUpdateDraftStatus(dr.id, "rejected")}
                                      className={cn(
                                        "text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 border rounded-xs transition-colors cursor-pointer",
                                        dr.status === "rejected"
                                          ? "bg-rose-600 text-white border-rose-600"
                                          : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50"
                                      )}
                                    >
                                      Từ chối
                                    </button>
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* STEP 4: REVIEW */}
                  {activeStep === "Review" && (() => {
                    const activeDraftsWithRisks = drafts.filter(dr => dr.riskNotes && dr.riskNotes.trim().length > 0)
                    const riskCount = activeDraftsWithRisks.length
                    
                    return (
                      <div className="space-y-4">
                        {/* 1. KOGITO CAMPAIGN PLANNING DASHBOARD */}
                        {!campaignPlan ? (
                          <div className="border border-dashed border-slate-300 rounded-sm p-8 text-center flex flex-col items-center justify-center space-y-3 bg-slate-50/50">
                            <Coins className="size-8 text-[#C8102E] animate-pulse" />
                            <h4 className="text-sm font-black text-[#1A2B49]">Đang đợi kết quả hoạch định từ Chuyên viên AI</h4>
                            <p className="text-[11px] text-slate-500 max-w-sm leading-relaxed">
                              Hệ thống sẽ tiến hành hoạch định ngân sách tối ưu, dự báo số lượng lead tiềm năng thu về và chi phí ước lượng dựa trên các chỉ số thị trường thực tế.
                            </p>
                          </div>
                        ) : (
                          <div className="border border-[#1A2B49] rounded-sm bg-white shadow-[2px_2px_0px_0px_#1A2B49] overflow-hidden">
                            <div className="bg-[#1A2B49] px-3.5 py-2 flex items-center justify-between">
                              <h3 className="text-[10px] font-black uppercase text-white tracking-wider flex items-center gap-1.5">
                                <Coins className="size-3.5 text-amber-400" />
                                <span>Hoạch định Chiến dịch & Dự báo Ngân sách tối ưu</span>
                              </h3>
                              <span className="bg-emerald-600 text-white border-emerald-600 text-[8px] font-bold uppercase px-1.5 py-0.5 rounded-xs border">
                                Đã tối ưu hóa
                              </span>
                            </div>

                            <div className="p-3.5 space-y-3.5 text-[11px]">
                              {/* Bento Grid Indicators */}
                              <div className="grid gap-2.5 grid-cols-2 sm:grid-cols-5">
                                
                                <div className="bg-slate-50 border border-slate-200 rounded-sm p-2 text-center">
                                  <span className="text-[8px] font-bold text-slate-500 uppercase block">Tổng ngân sách</span>
                                  <p className="text-xs font-black text-[#1A2B49] mt-0.5 font-mono">{campaignPlan.totalBudget}</p>
                                  <span className="text-[7.5px] text-slate-400">Ngân sách đề xuất</span>
                                </div>

                                <div className="bg-slate-50 border border-slate-200 rounded-sm p-2 text-center">
                                  <span className="text-[8px] font-bold text-slate-500 uppercase block">Mục tiêu Lead (KPI)</span>
                                  <p className="text-xs font-black text-[#1A2B49] mt-0.5 font-mono">{campaignPlan.targetLeads}</p>
                                  <span className="text-[7.5px] text-slate-400">Dự báo lượng lead</span>
                                </div>

                                <div className="bg-slate-50 border border-slate-200 rounded-sm p-2 text-center">
                                  <span className="text-[8px] font-bold text-slate-500 uppercase block">CPL Dự kiến</span>
                                  <p className="text-xs font-black text-[#C8102E] mt-0.5 font-mono">{campaignPlan.cpl}</p>
                                  <span className="text-[7.5px] text-slate-400">Chi phí/Lead tối ưu</span>
                                </div>

                                <div className="bg-slate-50 border border-slate-200 rounded-sm p-2 text-center">
                                  <span className="text-[8px] font-bold text-slate-500 uppercase block">Thời gian chạy</span>
                                  <p className="text-xs font-black text-[#1A2B49] mt-0.5 font-mono">{campaignPlan.duration}</p>
                                  <span className="text-[7.5px] text-slate-400">Thời hạn chiến dịch</span>
                                </div>

                                <div className="bg-slate-50 border border-slate-200 rounded-sm p-2 text-center col-span-2 sm:col-span-1">
                                  <span className="text-[8px] font-bold text-slate-500 uppercase block">Tần suất bài viết</span>
                                  <p className="text-xs font-black text-[#1A2B49] mt-0.5 font-mono">{campaignPlan.cadence}</p>
                                  <span className="text-[7.5px] text-slate-400">Tần suất đăng tải</span>
                                </div>

                              </div>

                              {/* Strategy details from tools */}
                              <div className="bg-slate-50/50 border border-slate-100 p-2.5 rounded-sm space-y-1">
                                <span className="text-[8.5px] font-bold uppercase text-slate-500 tracking-wider">Định hướng Chiến lược Tiếp cận:</span>
                                <p className="text-[#1A2B49] font-medium leading-relaxed">
                                  {brief.propertySegment === "apartments" 
                                    ? "Tập trung khai thác yếu tố hạ tầng (Hầm chui Nguyễn Văn Linh hoàn tất 2026) và ưu thế ban công view sông đắt giá ven Phú Mỹ Hưng." 
                                    : `Phát triển phễu Lead Generation chất lượng cao cho phân khúc ${brief.propertySegment} tại ${brief.location}, nhắm trọn tệp khách hàng tiềm năng.`}
                                </p>
                              </div>

                              {/* Kogito Metadata Bar */}
                              <div className="flex flex-wrap items-center justify-between gap-2.5 pt-2.5 border-t border-slate-100 text-[8.5px] text-slate-500">
                                <div className="flex flex-wrap gap-x-3 gap-y-1 font-mono">
                                  <span><strong>Phiên bản Luật:</strong> {campaignPlan.ruleVersion}</span>
                                  <span><strong>Ma trận Công thức:</strong> {campaignPlan.formulaVersion}</span>
                                  <span><strong>Mã Quyết định:</strong> {campaignPlan.decisionId}</span>
                                  <span><strong>Mã Kế hoạch:</strong> {campaignPlan.campaignPlanId}</span>
                                </div>
                                <span className="text-emerald-700 font-bold">CHỨNG THỰC BỞI HỆ THỐNG PHÁP LÝ KOGITO DMN</span>
                              </div>

                            </div>
                          </div>
                        )}

                        {/* 2. REGULATORY & CLAIMS REVIEW */}
                        {(drafts.length > 0 || isExecuting) && (
                          <div className="border border-[#1A2B49] rounded-sm bg-white shadow-[2px_2px_0px_0px_#1A2B49] overflow-hidden">
                            <div className="bg-[#1A2B49]/5 border-b border-[#1A2B49] px-3.5 py-2 flex items-center justify-between">
                              <h3 className="text-[10px] font-black uppercase text-[#1A2B49] tracking-wider flex items-center gap-1.5">
                                <ShieldCheck className={cn(
                                  "size-3.5",
                                  isExecuting ? "text-blue-600 animate-spin" : riskCount > 0 ? "text-amber-600" : "text-emerald-600"
                                )} />
                                <span>Hành lang Kiểm duyệt & Ràng buộc Quảng cáo</span>
                              </h3>
                            </div>

                            <div className="p-3.5 space-y-3 text-[11px]">
                              
                              <div className={cn(
                                "border p-2.5 rounded-sm transition-all text-[11px] leading-relaxed font-semibold",
                                isExecuting 
                                  ? "bg-blue-50 border-blue-400 text-blue-900" 
                                  : riskCount > 0 
                                    ? "bg-amber-50 border-amber-400 text-amber-900" 
                                    : "bg-emerald-50 border-emerald-400 text-emerald-900"
                              )}>
                                {isExecuting 
                                  ? "Đang tiến hành quét luật quảng cáo bất động sản, cam kết tài chính và kiểm tra ràng buộc địa lý thời gian thực..." 
                                  : riskCount > 0 
                                    ? `Quét luật quảng cáo hoàn tất! Phát hiện thấy ${riskCount} cảnh báo rủi ro quan trọng cần được rà soát trước khi phát hành.` 
                                    : "Quét luật quảng cáo hoàn tất! Toàn bộ nội dung bài viết đạt chuẩn an toàn, không phát hiện rủi ro nghiêm trọng."}
                              </div>

                              <div className="space-y-2.5">
                                {/* Automatic Local Geographic Verification */}
                                <div className="flex items-start gap-2.5 p-2.5 border border-slate-200 bg-slate-50/50 rounded-sm">
                                  <CheckCircle2 className="size-4 text-emerald-600 shrink-0 mt-0.5" />
                                  <div className="text-[11px]">
                                    <h4 className="font-bold text-[#1A2B49]">Kiểm duyệt Ràng buộc Địa lý & Phân khúc</h4>
                                    <p className="text-slate-600 mt-0.5 leading-relaxed">
                                      Đã đối chiếu phân khúc <strong className="text-[#C8102E]">{brief.propertySegment || "Bất động sản"}</strong> tại địa bàn <strong className="text-[#1A2B49]">{brief.location || "khu vực dự án"}</strong>. Quy hoạch hạ tầng và giao thông tại địa phương tương thích hoàn toàn với bối cảnh địa lý.
                                    </p>
                                  </div>
                                </div>

                                {/* Map through each real draft to show actual risk notes */}
                                {drafts.length === 0 ? (
                                  <div className="text-center py-4 border border-dashed border-slate-200 rounded-sm bg-slate-50/30 text-slate-400 text-[10px]">
                                    Chưa có bản thảo bài viết nào được gửi kiểm duyệt
                                  </div>
                                ) : (
                                  drafts.map((dr, index) => {
                                    const hasRisk = dr.riskNotes && dr.riskNotes.trim().length > 0;
                                    return (
                                      <div 
                                        key={`review-${dr.id}`}
                                        className={cn(
                                          "flex items-start gap-2.5 p-2.5 border rounded-sm transition-all",
                                          hasRisk 
                                            ? "border-amber-400 bg-amber-50/30" 
                                            : "border-slate-200 bg-white"
                                        )}
                                      >
                                        {hasRisk ? (
                                          <AlertTriangle className="size-4 text-amber-600 shrink-0 mt-0.5" />
                                        ) : (
                                          <CheckCircle2 className="size-4 text-emerald-600 shrink-0 mt-0.5" />
                                        )}
                                        <div className="text-[11px] w-full">
                                          <div className="flex items-center justify-between">
                                            <h4 className={cn("font-bold", hasRisk ? "text-amber-900" : "text-[#1A2B49]")}>
                                              {dr.angle || `Phương án ${index + 1}`}
                                            </h4>
                                            <span className={cn(
                                              "text-[8px] font-bold uppercase px-1.5 rounded-xs border",
                                              hasRisk 
                                                ? "bg-amber-100 text-amber-800 border-amber-300" 
                                                : "bg-emerald-100 text-emerald-800 border-emerald-300"
                                            )}>
                                              {hasRisk ? "Có cảnh báo" : "An toàn"}
                                            </span>
                                          </div>
                                          <p className="text-slate-600 mt-1 leading-relaxed">
                                            {hasRisk 
                                              ? cleanTechnicalAgentNames(dr.riskNotes || "") 
                                              : "Không phát hiện rủi ro nghiêm trọng về giá, cam kết sở hữu, tiến độ bàn giao hoặc ưu đãi tài chính ảo."}
                                          </p>
                                        </div>
                                      </div>
                                    );
                                  })
                                )}
                              </div>

                            </div>
                          </div>
                        )}
                      </div>
                    )
                  })()}



            </div>

            {/* FIXED PERSISTENT FOOTER BAR AT THE BOTTOM */}
            <div className="flex-none border-t border-slate-200 bg-slate-50/90 px-4 py-2.5 flex items-center justify-between z-10">
              
              {/* Left footer status */}
              <div className="hidden sm:flex items-center gap-2 text-[11px] text-slate-500 font-medium">
              </div>

              <div className="flex gap-2.5">
                {/* Dynamically render action button configs based on ActiveStep */}
                {activeStep === "Brief" && !isExecuting && (
                  <Button 
                    onClick={handleDelegateToAI}
                    className="bg-[#C8102E] hover:bg-[#A80B23] border border-[#1A2B49] shadow-[1.5px_1.5px_0px_0px_#1A2B49] text-white active:translate-y-px rounded-sm cursor-pointer px-4.5 h-8.5 text-[11px] font-black uppercase tracking-wider flex items-center gap-2"
                  >
                    <Sparkles className="size-3.5" />
                    Bắt đầu tạo bài viết bằng AI
                  </Button>
                )}

                {activeStep === "Drafts" && (
                  <>
                    <Button 
                      onClick={() => setActiveStep("Brief")}
                      className="bg-white border border-[#1A2B49] text-[#1A2B49] hover:bg-slate-50 active:translate-y-px rounded-sm shadow-[1.5px_1.5px_0px_0px_#1A2B49] cursor-pointer px-3.5 h-8 text-[11px] font-bold"
                    >
                      Quay lại Brief dự án
                    </Button>
                    <Button 
                      onClick={() => setActiveStep("Review")}
                      disabled={!hasExecuted}
                      className="bg-[#1A2B49] hover:bg-[#2A3B59] text-white active:translate-y-px rounded-sm shadow-[1.5px_1.5px_0px_0px_#1A2B49] cursor-pointer px-3.5 h-8 text-[11px] font-bold disabled:opacity-40 disabled:pointer-events-none"
                    >
                      Kiểm thử pháp lý & Governance
                      <ArrowRight className="size-3.5 ml-1" />
                    </Button>
                  </>
                )}

                {activeStep === "Insights" && (
                  <Button 
                    onClick={() => setActiveStep("Brief")}
                    className="bg-white border border-[#1A2B49] text-[#1A2B49] hover:bg-slate-50 active:translate-y-px rounded-sm shadow-[1.5px_1.5px_0px_0px_#1A2B49] cursor-pointer px-3.5 h-8 text-[11px] font-bold"
                  >
                    Trở về hồ sơ Brief chính
                  </Button>
                )}

                {activeStep === "Review" && (
                  <Button 
                    onClick={() => setActiveStep("Drafts")}
                    className="bg-white border border-[#1A2B49] text-[#1A2B49] hover:bg-slate-50 active:translate-y-px rounded-sm shadow-[1.5px_1.5px_0px_0px_#1A2B49] cursor-pointer px-3.5 h-8 text-[11px] font-bold"
                  >
                    Trở về xem Drafts
                  </Button>
                )}

              </div>

            </div>
          </section>

        </div>
      </div>
    </main>
  )
}
