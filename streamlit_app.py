"""
AmropaliNet — Streamlit Community Cloud entrypoint.

Modern green-themed dashboard: analyze first, Grad-CAM only on demand.
Supports both dark and light themes via CSS custom properties.
"""

from __future__ import annotations

import base64
import logging
import sys
import traceback
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

from inference import classify_image, generate_gradcam, is_mango
from model import CLASSES, DISEASE_INFO, load_model, load_mango_detector
from report import generate_report
from ui_render import (
    brand_html,
    classification_result_html,
    empty_result_html,
    encyclopedia_html,
    error_banner_html,
    file_chip_html,
    footer_html,
    gradcam_panel_html,
    probabilities_html,
    remedies_panel_html,
    side_title,
    upload_requirements_html,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent
DASH_CSS = (ROOT / "static" / "css" / "dashboard.css").read_text(encoding="utf-8")

ALLOWED_TYPES = ["png", "jpg", "jpeg", "webp", "bmp", "tiff", "tif"]
MAX_UPLOAD_MB = 10

# Light-theme variable overrides applied on :root so they always take effect
LIGHT_THEME_OVERRIDE = """
:root, html, body, .stApp, .main, [data-testid="stAppViewContainer"] {
    --bg-base: #f4f9f5;
    --bg-surface: #ffffff;
    --bg-card: rgba(255, 255, 255, 0.8);
    --bg-card-hover: rgba(255, 255, 255, 0.95);
    --bg-card-solid: #ffffff;
    --bg-input: #ffffff;
    --bg-overlay: rgba(244, 249, 245, 0.9);
    --border-subtle: rgba(34, 130, 70, 0.12);
    --border-medium: rgba(34, 130, 70, 0.22);
    --border-accent: rgba(34, 160, 80, 0.4);
    --border-error: rgba(220, 38, 38, 0.3);
    --text-primary: #1a2e22;
    --text-secondary: #4a6b55;
    --text-muted: #7a9985;
    --text-accent: #15803d;
    --text-error: #dc2626;
    --green-400: #22c55e;
    --green-500: #16a34a;
    --green-600: #15803d;
    --green-700: #166534;
    --green-800: #14532d;
    --green-900: #052e16;
    --gradient-brand: linear-gradient(135deg, #15803d, #16a34a, #22c55e);
    --gradient-brand-btn: linear-gradient(135deg, #16a34a, #15803d);
    --gradient-bar: linear-gradient(90deg, #15803d, #16a34a, #22c55e);
    --gradient-bar-dim: linear-gradient(90deg, rgba(22,163,74,0.3), rgba(34,197,94,0.12));
    --gradient-glow: 0 4px 20px rgba(22, 163, 74, 0.12);
    --gradient-glow-strong: 0 4px 28px rgba(22, 163, 74, 0.2);
    --shadow-card: 0 2px 12px rgba(0, 0, 0, 0.06);
    --shadow-card-hover: 0 8px 28px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(22,163,74,0.18);
    --shadow-btn: 0 4px 16px rgba(22, 163, 74, 0.2);
    --glass-bg: rgba(255, 255, 255, 0.65);
    --glass-blur: 12px;
    --glass-border: rgba(34, 130, 70, 0.12);
    --toggle-bg: rgba(34, 197, 94, 0.15);
    --toggle-knob: #16a34a;
    /* Override Streamlit config.toml dark theme tokens */
    --background-color: #f4f9f5 !important;
    --secondary-background-color: #ffffff !important;
    --text-color: #1a2e22 !important;
    --primary-color: #16a34a !important;
    color-scheme: light !important;
}

/* Native Streamlit widgets: kill residual dark surfaces in light mode */
.stApp [data-testid="stTextInput"] [data-baseweb="input"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1px solid rgba(34, 130, 70, 0.28) !important;
    box-shadow: none !important;
}
.stApp [data-testid="stTextInput"] [data-baseweb="base-input"],
.stApp [data-testid="stTextInput"] [data-baseweb="input"] > div,
.stApp [data-testid="stTextInput"] div[data-baseweb="base-input"] > div,
.stApp [data-testid="stTextInput"] input,
.stApp [data-testid="stTextInput"] textarea {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: #1a2e22 !important;
    caret-color: #1a2e22 !important;
}
.stApp [data-testid="stTextInput"] input::placeholder {
    color: #7a9985 !important;
    opacity: 1 !important;
}

/* Uploaded-file chip: force light surfaces over Streamlit base=dark */
.stApp [data-testid="stFileUploader"] section,
.stApp [data-testid="stFileUploader"] section > div,
.stApp [data-testid="stFileUploader"] [data-testid="stUploadedFile"],
.stApp [data-testid="stFileUploaderFile"],
.stApp [data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"],
.stApp [data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"],
.stApp [data-testid="stFileUploader"] [class*="uploadedFile"],
.stApp [data-testid="stFileUploader"] [class*="UploadedFile"],
.stApp [data-testid="stFileUploader"] li,
.stApp [data-testid="stFileUploaderDropzone"] {
    background: #eef7f1 !important;
    background-color: #eef7f1 !important;
    color: #1a2e22 !important;
    border-color: rgba(34, 130, 70, 0.25) !important;
}
.stApp [data-testid="stFileUploader"] [data-testid="stUploadedFile"] *,
.stApp [data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"],
.stApp [data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] *,
.stApp [data-testid="stFileUploader"] span,
.stApp [data-testid="stFileUploader"] small,
.stApp [data-testid="stFileUploader"] p,
.stApp [data-testid="stFileUploader"] button {
    color: #1a2e22 !important;
}
.stApp [data-testid="stFileUploader"] [data-testid="stUploadedFile"],
.stApp [data-testid="stFileUploaderFile"] {
    border: 1px solid rgba(34, 130, 70, 0.28) !important;
    border-radius: 10px !important;
}
.stApp .dash-toast,
.stApp .dash-toast.dash-error {
    background: #ffffff !important;
    border-color: rgba(220, 38, 38, 0.35) !important;
}
"""

st.set_page_config(
    page_title="AmropaliNet — Mango Disease Dashboard",
    page_icon="🥭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "theme" not in st.session_state:
    st.session_state.theme = "dark"


def inject_styles() -> None:
    theme = st.session_state.get("theme", "dark")
    extra = LIGHT_THEME_OVERRIDE if theme == "light" else ""
    scheme = "light" if theme == "light" else "dark"
    st.markdown(
        f"<style>\n{DASH_CSS}\n{extra}\n"
        f"html {{ color-scheme: {scheme}; }}\n"
        f"</style>",
        unsafe_allow_html=True,
    )
    if theme == "light":
        # Emotion-styled Streamlit chips ignore many CSS vars; force light paints in-DOM
        components.html(
            """
            <script>
            (function () {
              const doc = window.parent.document;
              function isDarkBg(el) {
                const bg = window.parent.getComputedStyle(el).backgroundColor || "";
                const m = bg.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/i);
                if (!m) return false;
                return (+m[1] + +m[2] + +m[3]) < 140;
              }
              function paint() {
                const roots = doc.querySelectorAll('[data-testid="stFileUploader"]');
                roots.forEach((root) => {
                  root.querySelectorAll("*").forEach((el) => {
                    if (isDarkBg(el)) {
                      el.style.setProperty("background", "#eef7f1", "important");
                      el.style.setProperty("background-color", "#eef7f1", "important");
                    }
                  });
                  root.querySelectorAll(
                    '[data-testid="stUploadedFile"], [data-testid="stFileUploaderFile"], [data-testid="stFileUploaderFileName"], span, small, p'
                  ).forEach((el) => {
                    el.style.setProperty("color", "#1a2e22", "important");
                  });
                });
              }
              paint();
              const obs = new MutationObserver(paint);
              obs.observe(doc.body, { childList: true, subtree: true });
            })();
            </script>
            """,
            height=0,
            width=0,
        )


def html(fragment: str) -> None:
    if fragment:
        st.html(fragment)


def trigger_pdf_download(pdf_bytes: bytes, filename: str) -> None:
    """Start a browser download immediately (no extra UI button)."""
    b64 = base64.b64encode(pdf_bytes).decode("ascii")
    safe_name = (
        "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in filename)
        or "AmropaliNet_Report.pdf"
    )
    components.html(
        f"""
        <html><body>
        <a id="amropali-pdf-dl" href="data:application/pdf;base64,{b64}" download="{safe_name}"></a>
        <script>
          const link = document.getElementById("amropali-pdf-dl");
          if (link) {{ link.click(); }}
        </script>
        </body></html>
        """,
        height=0,
        width=0,
    )


def render_header() -> None:
    """Brand bar + working light/dark theme toggle."""
    brand_col, toggle_col = st.columns([18, 1], gap="small", vertical_alignment="center")
    with brand_col:
        html(brand_html(st.session_state.theme))
    with toggle_col:
        is_light = st.session_state.theme == "light"
        label = "☀️" if is_light else "🌙"
        help_text = "Switch to dark theme" if is_light else "Switch to light theme"
        if st.button(
            label,
            key="theme_toggle",
            help=help_text,
            use_container_width=True,
        ):
            st.session_state.theme = "dark" if is_light else "light"
            st.rerun()


@st.cache_resource(show_spinner=False)
def get_aa_enet():
    return load_model()


@st.cache_resource(show_spinner=False)
def get_clip():
    return load_mango_detector()


def ensure_models_loaded() -> None:
    get_aa_enet()
    get_clip()


def run_classify(pil_img: Image.Image) -> tuple[dict | None, str | None]:
    """CLIP validation + AA-ENet classification only (no Grad-CAM)."""
    try:
        is_mango_pred, mango_conf = is_mango(pil_img)
        if not is_mango_pred:
            return None, (
                "This does not appear to be a mango. "
                "Please upload a clear photo of a mango fruit or mango leaf. "
                f"(mango confidence: {mango_conf * 100:.1f}%)"
            )

        classification = classify_image(pil_img)
        predicted = classification["predicted_class"]
        return {
            "classification": classification,
            "disease_info": DISEASE_INFO.get(predicted, {}),
            "gradcam": None,
        }, None
    except Exception:
        logger.error("Classify failed:\n%s", traceback.format_exc())
        return None, "Classification failed. Please try another image."


def run_gradcam_for_result(pil_img: Image.Image, predicted_class: str) -> dict:
    pred_idx = CLASSES.index(predicted_class)
    return generate_gradcam(pil_img, class_idx=pred_idx)


def open_uploaded_image(uploaded) -> Image.Image | None:
    try:
        return Image.open(uploaded).convert("RGB")
    except Exception:
        return None


# ── Shell ────────────────────────────────────────────────────────────────────
inject_styles()
render_header()

models_ok = True
try:
    with st.spinner("Loading models (first visit may take a minute)…"):
        ensure_models_loaded()
except Exception as exc:
    models_ok = False
    logger.error("Model load failed:\n%s", traceback.format_exc())
    html(error_banner_html(f"Failed to load models: {type(exc).__name__}: {exc}"))

left, right = st.columns([1, 2.5], gap="large")

# ── Left column ──────────────────────────────────────────────────────────────
with left:
    with st.container(border=True):
        html(side_title("📁", "Upload Mango Image"))
        uploaded = st.file_uploader(
            "Upload mango image",
            type=ALLOWED_TYPES,
            label_visibility="collapsed",
            key="mango_uploader",
        )
        if uploaded is not None:
            html(file_chip_html(uploaded.name, uploaded.size / (1024 * 1024)))
        html(upload_requirements_html())

    with st.container(border=True):
        html(side_title("⚙️", "Analysis Controls"))
        analyze = st.button(
            "🔬  Analyze & Classify",
            type="primary",
            use_container_width=True,
            disabled=not (models_ok and uploaded is not None),
            key="btn_analyze",
        )
        show_cam = st.button(
            "👁  GradCAM Visualization",
            type="secondary",
            use_container_width=True,
            disabled="result" not in st.session_state,
            key="btn_gradcam",
        )
        st.text_input(
            "Your name (for PDF report)",
            placeholder="Enter full name",
            max_chars=100,
            key="report_name",
        )
        gen_pdf = st.button(
            "📄  Download Report",
            use_container_width=True,
            disabled="result" not in st.session_state,
            key="btn_report",
        )

# ── File change resets ───────────────────────────────────────────────────────
if uploaded is not None:
    if uploaded.size > MAX_UPLOAD_MB * 1024 * 1024:
        html(error_banner_html(f"File too large. Maximum size is {MAX_UPLOAD_MB} MB."))
    else:
        file_key = f"{uploaded.name}:{uploaded.size}:{uploaded.type}"
        if st.session_state.get("upload_key") != file_key:
            st.session_state["upload_key"] = file_key
            st.session_state.pop("result", None)
            st.session_state.pop("pdf_bytes", None)
            st.session_state["show_gradcam"] = False

# ── Analyze only ─────────────────────────────────────────────────────────────
if analyze and models_ok and uploaded is not None:
    pil_img = open_uploaded_image(uploaded)
    if pil_img is None:
        html(error_banner_html("Could not read the image. Please upload a valid file."))
    else:
        with st.spinner("Validating mango → classifying with AA-ENet…"):
            result, err = run_classify(pil_img)
        if err:
            st.session_state.pop("result", None)
            st.session_state.pop("pdf_bytes", None)
            st.session_state["show_gradcam"] = False
            html(error_banner_html(err))
        else:
            st.session_state["result"] = result
            st.session_state["show_gradcam"] = False
            st.session_state.pop("pdf_bytes", None)
            logger.info(
                "Classification: %s (%.4f)",
                result["classification"]["predicted_class"],
                result["classification"]["confidence"],
            )
            st.rerun()

# ── Grad-CAM on demand ───────────────────────────────────────────────────────
if show_cam and "result" in st.session_state and uploaded is not None:
    pil_img = open_uploaded_image(uploaded)
    if pil_img is None:
        html(error_banner_html("Could not read the image for Grad-CAM."))
    else:
        result = st.session_state["result"]
        if not result.get("gradcam"):
            with st.spinner("Generating Grad-CAM visualization…"):
                result["gradcam"] = run_gradcam_for_result(
                    pil_img,
                    result["classification"]["predicted_class"],
                )
                st.session_state["result"] = result
        st.session_state["show_gradcam"] = True
        st.rerun()

# ── PDF generation + automatic download ──────────────────────────────────────
if gen_pdf and "result" in st.session_state:
    name = (st.session_state.get("report_name") or "").strip()
    if not name:
        html(error_banner_html("Please enter your name before generating the PDF report."))
    elif uploaded is None:
        html(error_banner_html("Please re-upload the image to generate the report."))
    else:
        result = st.session_state["result"]
        pil_img = open_uploaded_image(uploaded)
        try:
            with st.spinner("Preparing PDF report…"):
                if not result.get("gradcam") and pil_img is not None:
                    result["gradcam"] = run_gradcam_for_result(
                        pil_img,
                        result["classification"]["predicted_class"],
                    )
                    st.session_state["result"] = result
                if not result.get("gradcam"):
                    raise RuntimeError("Grad-CAM images unavailable")
                pdf_bytes = bytes(
                    generate_report(
                        user_name=name,
                        original_b64=result["gradcam"]["original_b64"],
                        heatmap_b64=result["gradcam"]["heatmap_b64"],
                        classification=result["classification"],
                        disease_info=result["disease_info"],
                    )
                )
            safe = "".join(
                ch if ch.isalnum() or ch in "-_ " else "_" for ch in name
            ).strip().replace(" ", "_")
            filename = f"AmropaliNet_Report_{safe}.pdf"
            st.session_state["pdf_bytes"] = pdf_bytes
            st.session_state["pdf_name"] = filename
            trigger_pdf_download(pdf_bytes, filename)
        except Exception:
            logger.error("Report failed:\n%s", traceback.format_exc())
            html(error_banner_html("Report generation failed. Please try again."))

# ── Right column ─────────────────────────────────────────────────────────────
with right:
    if "result" not in st.session_state:
        html(empty_result_html())
    else:
        result = st.session_state["result"]
        clf = result["classification"]
        info = result["disease_info"]

        html(classification_result_html(clf["predicted_class"], clf["confidence"], info))
        html(probabilities_html(clf["all_scores"]))

        # Grad-CAM appears before Diagnosis & Treatment when requested
        if st.session_state.get("show_gradcam") and result.get("gradcam"):
            gcam = result["gradcam"]
            html(gradcam_panel_html(gcam["original_b64"], gcam["heatmap_b64"]))

        html(remedies_panel_html(clf["predicted_class"], info))

html(encyclopedia_html())
html(footer_html())
