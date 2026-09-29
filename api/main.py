"""
mango-disease-ai — Public REST API
====================================
FastAPI server that exposes the mango disease analysis as HTTP endpoints.
Any mobile app, web app, or external system can call these over the internet.

Run locally:
    uvicorn api.main:app --reload --port 8000

Then visit: http://localhost:8000/docs  (interactive API documentation)
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from api.schemas import AnalyzeResponse, DiseaseListResponse, HealthResponse

# ── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Mango Disease AI API",
    description=(
        "AI-powered Amropali mango disease detection API.\n\n"
        "Upload a mango leaf/fruit image and receive:\n"
        "- Disease classification (7 classes)\n"
        "- Confidence scores for all classes\n"
        "- Grad-CAM heatmap visualization\n"
        "- Disease info: symptoms and treatment remedies\n"
        "- Downloadable PDF diagnosis report\n\n"
        "**Research Group**: AIUB R&D ICCA  \n"
        "**Model**: AA-ENet (EfficientNet-B0 + CBAM + Transformer)"
    ),
    version="0.1.0",
    contact={"name": "AIUB R&D ICCA Research Group"},
    license_info={"name": "MIT"},
)

# Allow cross-origin requests (so mobile apps and web apps can call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Any origin (mobile, web, Postman, etc.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the web frontend (templates/index.html + static/ assets)
_ROOT = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=_ROOT / "static"), name="static")


# ── Helper ────────────────────────────────────────────────────────────────────
def _read_upload(file: UploadFile) -> bytes:
    """Read uploaded file bytes and validate it's an image."""
    allowed = {"image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff"}
    if file.content_type and file.content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Upload JPEG, PNG, WebP, BMP, or TIFF.",
        )
    data = file.file.read()
    if len(data) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10 MB.")
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    return data


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    """Serve the AmropaliNet web app."""
    return FileResponse(_ROOT / "templates" / "index.html")


@app.get(
    "/api/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["System"],
)
async def health():
    """
    Check if the API server is running.

    Returns `{"status": "ok"}` when the server is healthy.
    Use this endpoint to verify connectivity before making analysis requests.
    """
    return {"status": "ok", "version": "0.1.0"}


@app.get(
    "/api/diseases",
    response_model=DiseaseListResponse,
    summary="List all diseases",
    tags=["Diseases"],
)
async def list_diseases():
    """
    Get information about all 7 detectable mango diseases.

    Returns a dictionary with disease names as keys, each containing:
    - Scientific name
    - Description
    - Symptoms list
    - Remedies / treatment recommendations
    """
    from mango_disease_ai.model import DISEASE_INFO
    return {"diseases": DISEASE_INFO}


@app.post(
    "/api/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze mango image",
    tags=["Analysis"],
)
async def analyze_image(
    image: UploadFile = File(..., description="Mango leaf or fruit image (JPEG/PNG/WebP, max 10 MB)"),
    include_gradcam: bool = Form(True, description="Include Grad-CAM heatmap in response (slower but visual)"),
):
    """
    Upload a mango image and get a full disease analysis.

    **Steps performed:**
    1. Validate that the image shows a mango (CLIP zero-shot detection)
    2. Classify the disease using AA-ENet (EfficientNet-B0 + CBAM + Transformer)
    3. Generate Grad-CAM++ heatmap showing which region triggered the diagnosis
    4. Return disease information with symptoms and treatment recommendations

    **Returns:**
    - `is_mango`: whether the image was validated as a mango
    - `predicted_class`: top disease prediction
    - `confidence`: prediction confidence (0.0–1.0)
    - `all_scores`: ranked list of all 7 class scores
    - `disease_info`: symptoms, remedies, scientific name
    - `gradcam_base64`: base64 PNG of the Grad-CAM heatmap overlay
    - `original_base64`: base64 PNG of the original (resized) image

    **Error codes:**
    - `400` — Invalid file (wrong type, too large, or corrupt)
    - `422` — Image is not a mango
    - `500` — Internal processing error
    """
    img_bytes = _read_upload(image)

    try:
        from mango_disease_ai import analyze
        result = analyze(img_bytes, include_gradcam=include_gradcam)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(exc)}")

    if not result["is_mango"]:
        raise HTTPException(
            status_code=422,
            detail=(
                f"This image does not appear to be a mango "
                f"(mango confidence: {result['mango_confidence']:.1%}). "
                "Please upload a clear photo of a mango leaf or fruit."
            ),
        )

    return result


@app.post(
    "/api/report",
    summary="Generate PDF diagnosis report",
    tags=["Analysis"],
    response_class=Response,
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "PDF report file download",
        },
        400: {"description": "Missing name or invalid file"},
        422: {"description": "Image is not a mango"},
        500: {"description": "Report generation failed"},
    },
)
async def generate_report(
    image: UploadFile = File(..., description="Mango leaf or fruit image (JPEG/PNG/WebP, max 10 MB)"),
    user_name: str = Form(..., description="Your name — will appear on the PDF report"),
):
    """
    Upload a mango image and download a professional PDF diagnosis report.

    The PDF includes:
    - Patient/user name and date
    - Disease prediction with confidence percentage
    - Classification scores table for all 7 classes
    - Original image and Grad-CAM heatmap side by side
    - Disease details: scientific name, description, symptoms, treatment
    - AI disclaimer footer

    **Returns:** PDF file (application/pdf) — directly downloadable.
    """
    if not user_name or not user_name.strip():
        raise HTTPException(status_code=400, detail="user_name is required and cannot be empty.")

    img_bytes = _read_upload(image)

    try:
        from mango_disease_ai import analyze, generate_pdf
        result = analyze(img_bytes, include_gradcam=True)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(exc)}")

    if not result["is_mango"]:
        raise HTTPException(
            status_code=422,
            detail=(
                f"This image does not appear to be a mango "
                f"(mango confidence: {result['mango_confidence']:.1%}). "
                "Please upload a clear photo of a mango leaf or fruit."
            ),
        )

    try:
        pdf_bytes = generate_pdf(result, user_name=user_name.strip())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(exc)}")

    # Sanitize user name for filename
    safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in user_name.strip())
    filename = f"mango_diagnosis_{safe_name}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
