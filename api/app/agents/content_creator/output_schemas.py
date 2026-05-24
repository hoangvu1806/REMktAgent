from pydantic import BaseModel, Field


class EvidenceSource(BaseModel):
    title: str = Field(default="", description="Source title or page title.")
    url: str = Field(default="", description="Clickable source URL.")
    source_type: str = Field(
        default="",
        description="Source category such as official, government, report, news, or listing.",
    )
    publisher: str = Field(default="", description="Publisher, organization, or website.")
    published_date: str = Field(default="", description="Publication date when available.")
    relevance: str = Field(default="", description="Why this source matters for the task.")
    confidence: str = Field(default="medium", description="high, medium, low, or cautious.")


class ResearchFinding(BaseModel):
    finding: str = Field(default="", description="Concise research finding.")
    label: str = Field(
        default="unavailable",
        description="source_backed, user_provided, assumption, or unavailable.",
    )
    confidence: str = Field(default="cautious", description="high, medium, low, or cautious.")
    source_urls: list[str] = Field(
        default_factory=list,
        description="URLs that support this finding. Required for source_backed labels.",
    )
    implications: list[str] = Field(
        default_factory=list,
        description="Implications for campaign angle, persona, or claim handling.",
    )
    caveats: list[str] = Field(
        default_factory=list,
        description="Limits, uncertainty, or risk notes for this finding.",
    )


class ApprovedSourceSearchOutput(BaseModel):
    search_focus: str = Field(default="", description="What the search attempted to verify.")
    summary: str = Field(default="", description="Short synthesis of useful evidence.")
    sources: list[EvidenceSource] = Field(default_factory=list)
    findings: list[ResearchFinding] = Field(default_factory=list)
    unavailable_signals: list[str] = Field(default_factory=list)
    next_search_queries: list[str] = Field(default_factory=list)


class LocalContextResearchOutput(BaseModel):
    location: str = Field(default="", description="Location or area researched.")
    summary: str = Field(default="", description="Short local context synthesis.")
    local_planning_and_infrastructure: list[ResearchFinding] = Field(default_factory=list)
    transport_and_amenities: list[ResearchFinding] = Field(default_factory=list)
    location_claim_cautions: list[str] = Field(default_factory=list)
    sources: list[EvidenceSource] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class MarketResearchOutput(BaseModel):
    summary: str = Field(default="", description="Short market insight synthesis.")
    research_questions: list[str] = Field(default_factory=list)
    demand_signals: list[ResearchFinding] = Field(default_factory=list)
    segment_or_pricing_context: list[ResearchFinding] = Field(default_factory=list)
    content_angle_opportunities: list[str] = Field(default_factory=list)
    sources: list[EvidenceSource] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class CompetitorPositioningOutput(BaseModel):
    comparison_scope: str = Field(default="", description="Location, segment, and price scope.")
    summary: str = Field(default="", description="Short competitor positioning synthesis.")
    competitor_signals: list[ResearchFinding] = Field(default_factory=list)
    positioning_patterns: list[str] = Field(default_factory=list)
    differentiation_opportunities: list[str] = Field(default_factory=list)
    sources: list[EvidenceSource] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
