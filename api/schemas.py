"""
Pydantic schemas for request/response validation in the mango-disease-ai API.
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., example="ok")
    version: str = Field(..., example="0.1.0")


class ClassScore(BaseModel):
    """Confidence score for a single disease class."""
    class_name: str = Field(..., alias="class", example="Anthracnose")
    score: float = Field(..., ge=0.0, le=1.0, example=0.9312)

    model_config = {"populate_by_name": True}


class DiseaseInfo(BaseModel):
    """Detailed information about a disease."""
    scientific_name: Optional[str] = Field(None, example="Colletotrichum gloeosporioides")
    description: Optional[str] = Field(None)
    symptoms: Optional[list[str]] = Field(None)
    remedies: Optional[list[str]] = Field(None)


class AnalyzeResponse(BaseModel):
    """Full response from the /api/analyze endpoint."""

    is_mango: bool = Field(
        ...,
        description="True if the image was validated as a mango by CLIP.",
        example=True,
    )
    mango_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="CLIP confidence that this is a mango image.",
        example=0.97,
    )
    predicted_class: Optional[str] = Field(
        None,
        description="Top predicted disease class.",
        example="Anthracnose",
    )
    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence of the top prediction.",
        example=0.9312,
    )
    all_scores: list[dict] = Field(
        default_factory=list,
        description="All 7 class scores sorted by confidence descending.",
    )
    disease_info: dict = Field(
        default_factory=dict,
        description="Disease details: scientific name, description, symptoms, remedies.",
    )
    gradcam_base64: Optional[str] = Field(
        None,
        description="Base64-encoded PNG of the Grad-CAM heatmap overlay. Decode and display as an image.",
    )
    original_base64: Optional[str] = Field(
        None,
        description="Base64-encoded PNG of the original (resized to 224×224) input image.",
    )


class DiseaseListResponse(BaseModel):
    """Response from the /api/diseases endpoint."""
    diseases: dict = Field(
        ...,
        description="Map of disease name → disease info (scientific name, description, symptoms, remedies).",
    )
