from typing import Any

from pydantic import BaseModel, Field

from app.models.insight import MarketAssumption
from app.models.project import PropertySegment


class CollectProjectFactsRequest(BaseModel):
    project_id: str
    brief: dict[str, Any]
    user_material_refs: list[str] = Field(default_factory=list)
    official_project_url: str | None = None


class CollectInsightWorkflowRequest(BaseModel):
    project_id: str
    approved_source_ids: list[str] = Field(default_factory=list)
    user_context: str | None = None
    official_project_url: str | None = None
    user_material_refs: list[str] = Field(default_factory=list)


class ConfirmMarketAssumptionsRequest(BaseModel):
    project_id: str
    insight_snapshot_id: str
    assumptions: list[MarketAssumption] = Field(default_factory=list)
    confirmed: bool = True


class PrepareCampaignContextRequest(BaseModel):
    project_id: str
    insight_summary: str
    insight_snapshot_id: str | None = None
    planning_constraints: dict[str, Any] = Field(default_factory=dict)
    unavailable_signals: list[str] = Field(default_factory=list)


class CreateProjectToolRequest(BaseModel):
    project_name: str = Field(min_length=1)
    property_segment: PropertySegment
    location: str = Field(min_length=1)
    price_range: str = Field(min_length=1)
    key_selling_points: list[str] = Field(min_length=1)
    campaign_objective: str = Field(min_length=1)
    buyer_profile: str = Field(min_length=1)
    tone: str = Field(min_length=1)
    promotion_details: str | None = None


class UpdateProjectToolRequest(CreateProjectToolRequest):
    project_id: str
