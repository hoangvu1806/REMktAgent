from enum import StrEnum

from pydantic import BaseModel, Field


class InsightLabel(StrEnum):
    source_backed = "source_backed"
    user_provided = "user_provided"
    unavailable = "unavailable"


class InsightStatus(StrEnum):
    idle = "idle"
    collecting = "collecting"
    partial = "partial"
    ready = "ready"
    failed = "failed"


class MarketSignal(BaseModel):
    signal_id: str
    signal_type: str
    label: InsightLabel
    summary: str
    source_id: str | None = None
    source_title: str | None = None
    source_url: str | None = None
    confidence: str = "medium"


class MarketAssumption(BaseModel):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class MarketInsightSnapshot(BaseModel):
    snapshot_id: str
    project_id: str
    status: InsightStatus
    summary: str
    signals: list[MarketSignal]
    assumptions: list[MarketAssumption]
    unavailable_signals: list[str]
    confirmed: bool
    created_at: str
    updated_at: str


class InsightCollectionRequest(BaseModel):
    user_context: str | None = None
    approved_source_ids: list[str] = Field(default_factory=list)


class UpdateAssumptionsRequest(BaseModel):
    assumptions: list[MarketAssumption] = Field(default_factory=list)
    confirmed: bool = False
