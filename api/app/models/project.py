from enum import StrEnum

from pydantic import BaseModel, Field


class PropertySegment(StrEnum):
    apartments = "apartments"
    land_plots = "land_plots"
    townhouses = "townhouses"
    villas_luxury = "villas_luxury"
    commercial_real_estate = "commercial_real_estate"


class ProjectBriefCreate(BaseModel):
    project_name: str = Field(min_length=1)
    property_segment: PropertySegment
    location: str = Field(min_length=1)
    price_range: str = Field(min_length=1)
    key_selling_points: list[str] = Field(min_length=1)
    campaign_objective: str = Field(min_length=1)
    buyer_profile: str = Field(min_length=1)
    tone: str = Field(min_length=1)
    promotion_details: str | None = None


class ProjectBrief(BaseModel):
    property_segment: PropertySegment
    location: str
    price_range: str
    key_selling_points: list[str]
    campaign_objective: str
    buyer_profile: str
    tone: str
    promotion_details: str | None = None


class Project(BaseModel):
    project_id: str
    project_name: str
    brief: ProjectBrief
    created_at: str
    updated_at: str
