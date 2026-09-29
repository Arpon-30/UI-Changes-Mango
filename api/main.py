"""
mango-disease-ai - Web app + REST API
=====================================
FastAPI server that serves the AmropaliNet website and the analysis API.

Run locally:
    python run.py                                  (opens the browser)
    uvicorn api.main:app --reload --port 8000

Then visit: http://localhost:8000  (website)  ·  http://localhost:8000/docs  (API docs)
"""

from __future__ import annotations

import os

# This project uses PyTorch only. Stop `transformers` from importing TensorFlow/Keras
# when they happen to be installed in the same environment (e.g. a TF conda env).
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_TORCH", "1")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

import io
import logging
import re
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from api.schemas import AnalyzeResponse, DiseaseListResponse, HealthResponse

log = logging.getLogger("amropalinet")

# ── Model status (filled by the start-up warm-up) ───────────────────────────
_status = {
    "model": "loading",
    "model_error": None,
    "mango_check": "loading",
    "mango_check_error": None,
}
# Grad-CAM toggles gradients on the shared model, so run one analysis at a time.
_analysis_lock = threading.Lock()

CLIP_HELP = (
    "The mango checker (CLIP) could not be loaded. On the first scan it downloads about "
    "600 MB from Hugging Face, so the computer needs internet once."
)


def _load_mango_checker():
    from mango_disease_ai.model import load_mango_detector

    try:
        load_mango_detector()
        _status.update(mango_check="ok", mango_check_error=None)
    except Exception as exc:  # network / Hugging Face problems
        _status.update(mango_check="error", mango_check_error=f"{CLIP_HELP} Details: {exc}")
        raise


def _warm_up():
    """Load AA-ENet and CLIP in the background so the first scan is fast."""
    try:
        from mango_disease_ai.model import load_model

        load_model()
        _status.update(model="ok", model_error=None)
        log.info("AA-ENet model loaded")
    except Exception as exc:
        _status.update(model="error", model_error=str(exc))
        log.error("AA-ENet model NOT loaded: %s", exc)
    try:
        _load_mango_checker()
        log.info("CLIP mango checker loaded")
    except Exception as exc:
        log.error("CLIP mango checker NOT loaded: %s", exc)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    threading.Thread(target=_warm_up, daemon=True).start()
    yield


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
    version="0.2.0",
    contact={"name": "AIUB R&D ICCA Research Group"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

# Allow cross-origin requests (so mobile apps and web apps can call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the web frontend (templates/index.html + static/ assets)
_ROOT = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=_ROOT / "static"), name="static")


# ── Helpers ──────────────────────────────────────────────────────────────────
def _fail(status: int, code: str, message: str, **extra):
    """Raise an error the website can recognise (detail.code) and explain."""
    raise HTTPException(status_code=status, detail={"code": code, "message": message, **extra})


def _read_upload(file: UploadFile) -> bytes:
    """Read the uploaded file and make sure it is a readable image."""
    allowed = {"image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff"}
    if file.content_type and file.content_type not in allowed:
        _fail(400, "bad_type", f"Unsupported file type: {file.content_type}. Upload JPEG, PNG, WebP, BMP, or TIFF.")
    data = file.file.read()
    if len(data) > 10 * 1024 * 1024:
        _fail(400, "too_large", "File too large. Maximum size is 10 MB.")
    if not data:
        _fail(400, "empty", "Uploaded file is empty.")
    try:
        from PIL import Image

        Image.open(io.BytesIO(data)).verify()
    except Exception:
        _fail(400, "bad_image", "This file could not be read as an image.")
    return data


def _run_analysis(img_bytes: bytes) -> dict:
    """Mango check (CLIP) -> AA-ENet -> Grad-CAM, with clear errors for each failure."""
    from mango_disease_ai.model import ModelNotReadyError, resolve_model_path

    try:
        resolve_model_path()
    except ModelNotReadyError as exc:
        _fail(503, "model_missing", str(exc))

    if _status["mango_check"] != "ok":
        try:
            _load_mango_checker()
        except Exception:
            _fail(503, "mango_check_unavailable", _status["mango_check_error"] or CLIP_HELP)

    try:
        from mango_disease_ai import analyze

        with _analysis_lock:
            result = analyze(img_bytes, include_gradcam=True)
    except ModelNotReadyError as exc:
        _fail(503, "model_missing", str(exc))
    except Exception as exc:
        log.exception("Analysis failed")
        _fail(500, "analysis_failed", f"Analysis failed: {exc}")

    _status.update(model="ok", model_error=None)

    if not result["is_mango"]:
        _fail(
            422,
            "not_mango",
            "This image does not appear to be a mango. Please upload a clear photo of a mango fruit or leaf.",
            mango_confidence=result["mango_confidence"],
        )
    return result


# ── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    """Serve the AmropaliNet web app."""
    return FileResponse(_ROOT / "templates" / "index.html")


@app.get("/api/health", response_model=HealthResponse, summary="Health check", tags=["System"])
def health():
    """
    Server status plus whether the AI models are ready.

    `model` / `mango_check` are `loading`, `ok` or `error`; the `*_error` fields explain problems.
    """
    return {"status": "ok", "version": app.version, **_status}


@app.get("/api/diseases", response_model=DiseaseListResponse, summary="List all diseases", tags=["Diseases"])
def list_diseases():
    """Information about all 7 classes: scientific name, description, symptoms, remedies."""
    from mango_disease_ai.model import DISEASE_INFO

    return {"diseases": DISEASE_INFO}


@app.post("/api/analyze", response_model=AnalyzeResponse, summary="Analyze mango image", tags=["Analysis"])
def analyze_image(
    image: UploadFile = File(..., description="Mango leaf or fruit image (JPEG/PNG/WebP, max 10 MB)"),
):
    """
    Upload a mango image and get a full disease analysis:
    mango check (CLIP) -> disease class (AA-ENet) -> Grad-CAM++ heatmap -> disease info.

    **Error codes** (`detail.code` in the JSON body):
    - `400` bad_type / too_large / empty / bad_image
    - `422` not_mango (also returns `mango_confidence`)
    - `503` model_missing / mango_check_unavailable
    - `500` analysis_failed
    """
    return _run_analysis(_read_upload(image))


@app.post(
    "/api/report",
    summary="Generate PDF diagnosis report",
    tags=["Analysis"],
    response_class=Response,
    responses={200: {"content": {"application/pdf": {}}, "description": "PDF report file download"}},
)
def generate_report(
    image: UploadFile = File(..., description="Mango leaf or fruit image (JPEG/PNG/WebP, max 10 MB)"),
    user_name: str = Form(..., description="Name printed on the PDF report"),
):
    """Analyze the image and return a PDF report (result, scores, Grad-CAM, symptoms, treatment)."""
    if not user_name or not user_name.strip():
        _fail(400, "no_name", "user_name is required and cannot be empty.")

    result = _run_analysis(_read_upload(image))

    try:
        from mango_disease_ai import generate_pdf

        pdf_bytes = generate_pdf(result, user_name=user_name.strip())
    except Exception as exc:
        log.exception("PDF generation failed")
        _fail(500, "report_failed", f"PDF generation failed: {exc}")

    # HTTP headers must be ASCII: plain fallback name + UTF-8 name (e.g. Bangla) per RFC 5987
    name = user_name.strip()
    ascii_name = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_") or "report"
    disposition = (
        f'attachment; filename="AmropaliNet_Report_{ascii_name}.pdf"; '
        f"filename*=UTF-8''{quote('AmropaliNet_Report_' + name + '.pdf')}"
    )
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": disposition})
