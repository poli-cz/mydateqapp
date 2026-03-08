from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class AnalyzeProfileInput(BaseModel):
    platform: str = Field(default="hinge")
    photo_count: int = Field(default=0, ge=0, le=6)
    bio: str = Field(default="")
    prompts: list[str] = Field(default_factory=list)
    photo_filenames: list[str] = Field(default_factory=list)
    source: Literal["json", "multipart", "demo"] = "json"


class PhotoScorePreview(BaseModel):
    label: str
    score: float
    note: str


class OpenerItem(BaseModel):
    prompt: str
    text: str


class LookingForTag(BaseModel):
    emoji: str
    label: str


class FreeReport(BaseModel):
    score: float
    headline: str
    hinge_tip: str
    bio_before: str
    bio_after_preview: str
    photo_scores_preview: list[PhotoScorePreview]
    openers_preview: list[OpenerItem]
    projected_score: float


class PhotoBreakdownItem(BaseModel):
    label: str
    score: float
    note: str
    action: str


class ProReport(BaseModel):
    looking_for_tags: list[LookingForTag]
    target_audience: str
    bio_rewrite: str
    photo_breakdown: list[PhotoBreakdownItem]
    openers: list[OpenerItem]
    projected_score: float


class AnalysisResponse(BaseModel):
    analysis_id: str
    paid: bool = False
    profile: dict[str, Any]
    free_report: FreeReport
    pro_report: ProReport
    # Legacy fields kept so the current FE / old clients do not break immediately.
    dq_score: float
    verdict: str
    platform: str
    breakdown: dict[str, float]
    notes: list[str]
