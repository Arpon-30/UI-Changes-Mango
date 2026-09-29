"""
mango_disease_ai.server
=======================
Built-in FastAPI REST server — bundled directly inside the PyPI package.

Any developer can start this server with ONE command after pip install:

    # Method 1 — Python module (works anywhere, no folder needed)
    python -m mango_disease_ai.server

    # Method 2 — Console script (installed automatically with pip)
    mango-api

    # Method 3 — With custom port
    python -m mango_disease_ai.server --port 8080

Then open in browser:
    http://localhost:8000         <- Welcome page
    http://localhost:8000/guide   <- Animated documentation
    http://localhost:8000/docs    <- Swagger UI (interactive testing)
    http://localhost:8000/api/health
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    version: str

class ScoreItem(BaseModel):
    class_name: str
    score: float

class AnalyzeResponse(BaseModel):
    is_mango: bool
    mango_confidence: float
    predicted_class: str | None = None
    confidence: float | None = None
    all_scores: list[dict] | None = None
    disease_info: dict | None = None
    gradcam_base64: str | None = None
    original_base64: str | None = None

class DiseaseListResponse(BaseModel):
    diseases: dict


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Mango Disease AI API",
    description=(
        "AI-powered Amropali mango disease detection API.\n\n"
        "Upload a mango leaf or fruit image and receive:\n"
        "- **Disease classification** (7 classes)\n"
        "- **Confidence scores** for all classes\n"
        "- **Grad-CAM++ heatmap** visualization\n"
        "- **PDF diagnosis report** download\n\n"
        "**Install:** `pip install mango-disease-ai[api]`  \n"
        "**Start:** `mango-api` or `python -m mango_disease_ai.server`  \n"
        "**Research Group:** AIUB R&D ICCA  \n"
        "**Model:** AA-ENet (EfficientNet-B0 + CBAM + Transformer)"
    ),
    version="0.1.3",
    contact={"name": "AIUB R&D ICCA Research Group"},
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
ALLOWED_CONTENT_TYPES = {
    "image/jpeg", "image/jpg", "image/png",
    "image/webp", "image/bmp", "image/tiff",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _read_upload(file: UploadFile) -> bytes:
    if file.content_type and file.content_type.lower() not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: '{file.content_type}'. Upload JPEG, PNG, WebP, BMP or TIFF.",
        )
    data = file.file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 10 MB.")
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    return data


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/guide", response_class=HTMLResponse, include_in_schema=False)
async def guide():
    """Serve the animated docs website bundled inside the package."""
    # Try package-bundled docs first
    pkg_docs = Path(__file__).parent / "docs.html"
    if pkg_docs.exists():
        return HTMLResponse(content=pkg_docs.read_text(encoding="utf-8"))
    # Fallback: look in cwd
    cwd_docs = Path.cwd() / "docs.html"
    if cwd_docs.exists():
        return HTMLResponse(content=cwd_docs.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>docs.html not found</h1>", status_code=404)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """Welcome page."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mango Disease AI API</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Segoe UI',sans-serif;background:#0d1117;color:#e6edf3;
         display:flex;align-items:center;justify-content:center;min-height:100vh}
    .card{background:#161b22;border:1px solid #30363d;border-radius:16px;
          padding:48px 56px;max-width:600px;width:90%;text-align:center;
          box-shadow:0 8px 32px rgba(0,0,0,.4)}
    .emoji{font-size:3rem;margin-bottom:12px}
    h1{color:#3fb950;font-size:2rem;margin-bottom:8px}
    .version{color:#8b949e;font-size:.85rem;margin-bottom:16px}
    p{color:#8b949e;line-height:1.7;margin-bottom:20px}
    .install{background:#0d1117;border:1px solid #30363d;border-radius:8px;
             padding:12px 16px;font-family:monospace;font-size:.85rem;
             color:#a5d6ff;margin:16px 0;text-align:left}
    .badges{margin:16px 0 28px}
    .badge{display:inline-block;background:#1f6feb22;border:1px solid #1f6feb55;
           color:#79c0ff;border-radius:6px;padding:4px 12px;font-size:.78rem;margin:4px}
    .buttons{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-bottom:24px}
    a.btn{display:inline-block;padding:12px 28px;border-radius:8px;font-weight:600;
          text-decoration:none;font-size:.95rem;transition:opacity .2s}
    a.btn:hover{opacity:.85}
    .btn-primary{background:#3fb950;color:#0d1117}
    .btn-guide{background:#7c3aed;color:#fff}
    .btn-outline{background:transparent;color:#79c0ff;border:1px solid #1f6feb}
    .endpoints{margin-top:24px;text-align:left;background:#0d1117;border:1px solid #30363d;
               border-radius:8px;padding:16px 20px}
    .endpoints h3{color:#79c0ff;font-size:.85rem;margin-bottom:10px;letter-spacing:.05em}
    .endpoint{display:flex;align-items:center;gap:10px;padding:5px 0;font-size:.82rem;
              border-bottom:1px solid #21262d}
    .endpoint:last-child{border-bottom:none}
    .method{font-weight:700;min-width:40px;font-size:.75rem}
    .get{color:#3fb950}.post{color:#e3b341}
    .path{color:#e6edf3;font-family:monospace}
    .desc{color:#8b949e}
  </style>
</head>
<body>
  <div class="card">
    <div class="emoji">&#129389;</div>
    <h1>Mango Disease AI</h1>
    <div class="version">v0.1.2 &bull; AIUB R&amp;D ICCA Research Group</div>
    <p>AI-powered Amropali mango disease detection API.<br>
       Detect 7 diseases with Grad-CAM heatmaps &amp; PDF reports.</p>
    <div class="install">pip install mango-disease-ai[api]<br>mango-api</div>
    <div class="badges">
      <span class="badge">AA-ENet Model</span>
      <span class="badge">CLIP Validation</span>
      <span class="badge">Grad-CAM++</span>
      <span class="badge">PDF Reports</span>
      <span class="badge">7 Disease Classes</span>
    </div>
    <div class="buttons">
      <a class="btn btn-primary" href="/docs">&#128216; Swagger UI</a>
      <a class="btn btn-guide" href="/guide">&#128214; Full Docs</a>
      <a class="btn btn-outline" href="/api/health">&#10084;&#65039; Health</a>
    </div>
    <div class="endpoints">
      <h3>AVAILABLE ENDPOINTS</h3>
      <div class="endpoint"><span class="method get">GET</span><span class="path">/api/health</span><span class="desc"> &mdash; Server health check</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="path">/api/diseases</span><span class="desc"> &mdash; All 7 disease info</span></div>
      <div class="endpoint"><span class="method post">POST</span><span class="path">/api/analyze</span><span class="desc"> &mdash; Image &rarr; JSON diagnosis</span></div>
      <div class="endpoint"><span class="method post">POST</span><span class="path">/api/report</span><span class="desc"> &mdash; Image + name &rarr; PDF</span></div>
      <div class="endpoint"><span class="method get">GET</span><span class="path">/guide</span><span class="desc"> &mdash; Animated documentation</span></div>
    </div>
  </div>
</body>
</html>"""


@app.get("/api/health", response_model=HealthResponse, tags=["System"], summary="Health check")
async def health():
    """Returns OK when the server is running."""
    from mango_disease_ai import __version__
    return {"status": "ok", "version": __version__}


@app.get("/api/diseases", tags=["Diseases"], summary="List all 7 detectable diseases")
async def list_diseases():
    """Get full info for all 7 disease classes: name, symptoms, remedies."""
    from mango_disease_ai.model import DISEASE_INFO
    return {"diseases": DISEASE_INFO}


@app.post(
    "/api/analyze",
    response_model=AnalyzeResponse,
    tags=["Analysis"],
    summary="Analyze a mango image for disease",
    responses={
        200: {"description": "Successful diagnosis"},
        400: {"description": "Invalid file"},
        422: {"description": "Not a mango image"},
        500: {"description": "AI processing error"},
    },
)
async def analyze_image(
    image: UploadFile = File(..., description="Mango leaf/fruit image. JPEG/PNG/WebP/BMP. Max 10 MB."),
    include_gradcam: bool = Form(True, description="Include Grad-CAM heatmap? True=slower, False=faster."),
):
    """Upload a mango image → get full disease classification + optional heatmap."""
    img_bytes = _read_upload(image)
    try:
        from mango_disease_ai import analyze
        result = analyze(img_bytes, include_gradcam=include_gradcam)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {type(exc).__name__}: {exc}")

    if not result["is_mango"]:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Not a mango (confidence: {result['mango_confidence']:.1%}). "
                "Upload a clear mango leaf or fruit photo."
            ),
        )
    return result


@app.post(
    "/api/report",
    tags=["Analysis"],
    summary="Generate a PDF diagnosis report",
    response_class=Response,
    responses={
        200: {"content": {"application/pdf": {}}, "description": "PDF file"},
        400: {"description": "Invalid input"},
        422: {"description": "Not a mango"},
        500: {"description": "Processing error"},
    },
)
async def generate_report(
    image: UploadFile = File(..., description="Mango image. Max 10 MB."),
    user_name: str = Form(..., description="Your name for the PDF header. E.g. Dr. Rahman"),
):
    """Upload image + your name → download a professional PDF diagnosis report."""
    if not user_name or not user_name.strip():
        raise HTTPException(status_code=400, detail="user_name is required.")

    img_bytes = _read_upload(image)
    try:
        from mango_disease_ai import analyze, generate_pdf
        result = analyze(img_bytes, include_gradcam=True)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")

    if not result["is_mango"]:
        raise HTTPException(
            status_code=422,
            detail=f"Not a mango (confidence: {result['mango_confidence']:.1%}).",
        )

    try:
        pdf_bytes = generate_pdf(result, user_name=user_name.strip())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {exc}")

    safe = "".join(c if c.isalnum() or c in "-_ " else "_" for c in user_name.strip()).replace(" ", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="mango_diagnosis_{safe}.pdf"'},
    )


# ---------------------------------------------------------------------------
# CLI entry point  (python -m mango_disease_ai.server  OR  mango-api)
# ---------------------------------------------------------------------------
def main():
    """Console script entry point: `mango-api`"""
    try:
        import uvicorn
    except ImportError:
        print("\n[ERROR] uvicorn is not installed.")
        print("Run: pip install mango-disease-ai[api]")
        print("  or: pip install fastapi uvicorn[standard] python-multipart\n")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        prog="mango-api",
        description="Mango Disease AI — REST API Server",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (dev mode)")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  🥭  Mango Disease AI -- REST API Server v0.1.3")
    print("=" * 60)
    print(f"  Starting on  http://{args.host}:{args.port}")
    print(f"  Welcome page http://localhost:{args.port}")
    print(f"  Swagger UI   http://localhost:{args.port}/docs")
    print(f"  Full Docs    http://localhost:{args.port}/guide")
    print(f"  Health       http://localhost:{args.port}/api/health")
    print("  Press CTRL+C to stop.")
    print("=" * 60 + "\n")

    uvicorn.run(
        "mango_disease_ai.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
