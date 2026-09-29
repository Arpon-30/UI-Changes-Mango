"""
PDF diagnosis report for AmropaliNet (one A4 page).

Layout: brand header · who/when · diagnosis card · photo / heatmap / marked area ·
about the disease · signs + treatment · all class scores · disclaimer footer.
"""

from __future__ import annotations

import base64
import io
import uuid
from datetime import datetime

from fpdf import FPDF

# ── Brand ────────────────────────────────────────────────────────────────────
GREEN_DARK = (27, 94, 32)
GREEN = (46, 125, 50)
GREEN_TINT = (241, 247, 232)
MANGO = (251, 140, 0)
INK = (29, 58, 31)
INK_SOFT = (78, 107, 74)
MUTED = (120, 135, 115)
BORDER = (220, 235, 205)
RED = (198, 40, 40)

TEAM_LINE = (
    "AIUB Student Group (Arpon, Oni, Md. Ibtihazzaman) - "
    "Supervised by Dr. Md. Saef Ullah Miah - arponamit.55@gmail.com"
)
DISCLAIMER = (
    "For guidance only. This report is produced by an AI model and can be wrong. "
    "Always consult a qualified agronomist for crop management decisions."
)

DISEASE_STYLE = {
    "Anthracnose": ((181, 84, 28), "High"),
    "Bacterial Canker": ((142, 106, 0), "High"),
    "Healthy": ((46, 125, 50), "None"),
    "Powdery Mildew": ((96, 112, 130), "High"),
    "Scab": ((141, 110, 99), "Medium"),
    "Sooty Mould": ((55, 71, 79), "Medium"),
    "Stem End Rot": ((93, 64, 55), "High"),
}

# A4 portrait, millimetres
PAGE_W, PAGE_H = 210, 297
MARGIN = 14
CONTENT_W = PAGE_W - 2 * MARGIN


def _clean(text) -> str:
    """Core PDF fonts are Latin-1 only: normalise dashes/quotes, drop other scripts."""
    s = str(text or "")
    for a, b in {"–": "-", "—": "-", "‘": "'", "’": "'",
                 "“": '"', "”": '"', "…": "...", "×": "x"}.items():
        s = s.replace(a, b)
    s = "".join(ch for ch in s if ch.encode("latin-1", "ignore"))
    return " ".join(s.split())


def _pdf_name(name: str) -> str:
    return _clean(name) or "Farmer"


def _img(b64: str | None):
    return io.BytesIO(base64.b64decode(b64)) if b64 else None


class _ReportPDF(FPDF):
    def footer(self):
        self.set_y(-22)
        self.set_draw_color(*BORDER)
        self.line(MARGIN, self.get_y(), PAGE_W - MARGIN, self.get_y())
        self.ln(2)
        self.set_font("Helvetica", "I", 7.5)
        self.set_text_color(*MUTED)
        self.multi_cell(CONTENT_W, 3.6, DISCLAIMER, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 7.5)
        self.multi_cell(CONTENT_W, 3.6, TEAM_LINE, align="C", new_x="LMARGIN", new_y="NEXT")


def _heading(pdf: FPDF, text: str, y: float | None = None, x: float = MARGIN, w: float = CONTENT_W) -> None:
    if y is not None:
        pdf.set_xy(x, y)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(*GREEN_DARK)
    pdf.cell(w, 6, _clean(text), new_x="LEFT", new_y="NEXT")


def _bullets(pdf: FPDF, items, x: float, y: float, w: float, numbered: bool = False) -> float:
    """Draw a bullet / numbered list inside a column, return the bottom y."""
    for i, item in enumerate(items, 1):
        pdf.set_xy(x, y)
        pdf.set_text_color(*(GREEN if numbered else MANGO))
        pdf.set_font("Helvetica", "B", 8.8)
        pdf.cell(5, 4.4, f"{i}." if numbered else "-")
        pdf.set_font("Helvetica", "", 8.8)
        pdf.set_text_color(*INK)
        pdf.set_xy(x + 5, y)
        pdf.multi_cell(w - 5, 4.4, _clean(item), new_x="LMARGIN", new_y="NEXT")
        y = pdf.get_y() + 1
    return y


def generate_report(
    user_name: str,
    original_b64: str,
    heatmap_b64: str,
    classification: dict,
    disease_info: dict | None = None,
    marked_b64: str | None = None,
    affected_percent: float | None = None,
) -> bytes:
    """Build the one-page PDF and return its bytes."""
    disease_info = disease_info or {}
    pred = classification["predicted_class"]
    conf = float(classification["confidence"])
    tone, risk = DISEASE_STYLE.get(pred, (GREEN, "-"))
    healthy = pred == "Healthy"

    pdf = _ReportPDF(format="A4")
    pdf.set_margins(MARGIN, MARGIN, MARGIN)
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    # ── Header band ──────────────────────────────────────────────────────
    pdf.set_fill_color(*GREEN_DARK)
    pdf.rect(0, 0, PAGE_W, 28, style="F")
    pdf.set_fill_color(*MANGO)
    pdf.rect(0, 28, PAGE_W, 1.4, style="F")
    pdf.set_xy(MARGIN, 7)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(100, 9, "AmropaliNet")
    pdf.set_xy(MARGIN, 16)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(220, 240, 210)
    pdf.cell(100, 5, "Amrapali Mango Disease Report")

    now = datetime.now()
    report_id = uuid.uuid4().hex[:8].upper()
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_xy(PAGE_W - MARGIN - 70, 8)
    pdf.cell(70, 5, now.strftime("%d %B %Y, %I:%M %p"), align="R")
    pdf.set_xy(PAGE_W - MARGIN - 70, 14)
    pdf.cell(70, 5, f"Report ID: {report_id}", align="R")

    # ── Prepared for ─────────────────────────────────────────────────────
    y = 35
    pdf.set_xy(MARGIN, y)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*MUTED)
    pdf.cell(24, 5, "Prepared for")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*INK)
    pdf.cell(100, 5, _pdf_name(user_name))

    # ── Diagnosis card ───────────────────────────────────────────────────
    y = 44
    card_h = 30
    pdf.set_fill_color(*GREEN_TINT)
    pdf.set_draw_color(*BORDER)
    pdf.rect(MARGIN, y, CONTENT_W, card_h, style="DF", round_corners=True, corner_radius=3)
    pdf.set_fill_color(*tone)
    pdf.rect(MARGIN, y, 3, card_h, style="F")

    pdf.set_xy(MARGIN + 8, y + 4)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(*MANGO)
    pdf.cell(80, 4, "DIAGNOSIS")
    pdf.set_xy(MARGIN + 8, y + 9)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*tone)
    pdf.cell(110, 9, "Healthy mango" if healthy else _clean(pred))
    pdf.set_xy(MARGIN + 8, y + 19)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*INK_SOFT)
    pdf.cell(110, 5, _clean(disease_info.get("scientific_name", "")))

    # confidence + risk on the right
    rx = PAGE_W - MARGIN - 58
    pdf.set_xy(rx, y + 5)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*INK)
    pdf.cell(52, 9, f"{conf * 100:.1f}%", align="R")
    pdf.set_xy(rx, y + 14)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*MUTED)
    pdf.cell(52, 4, "AI confidence", align="R")
    pdf.set_xy(rx, y + 20)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*(RED if risk == "High" else GREEN if risk == "None" else MANGO))
    pdf.cell(52, 5, f"Garden risk: {risk}", align="R")

    y += card_h + 3
    if conf < 0.7:
        pdf.set_xy(MARGIN, y)
        pdf.set_font("Helvetica", "I", 8.5)
        pdf.set_text_color(*MANGO)
        pdf.multi_cell(CONTENT_W, 4.2, "The AI is not fully sure. Take another photo in daylight, closer to the spot, "
                       "and compare with the signs below.", new_x="LMARGIN", new_y="NEXT")
        y = pdf.get_y() + 1

    # ── Images ───────────────────────────────────────────────────────────
    y += 2
    gap = 5
    img_w = (CONTENT_W - 2 * gap) / 3
    panels = [
        (original_b64, "Your photo"),
        (heatmap_b64, "Where the AI looked (Grad-CAM)"),
        (marked_b64 if not healthy else original_b64,
         "Likely affected area" if not healthy else "No affected area"),
    ]
    for i, (b64, caption) in enumerate(panels):
        x = MARGIN + i * (img_w + gap)
        data = _img(b64)
        if data:
            pdf.image(data, x=x, y=y, w=img_w, h=img_w)
        pdf.set_draw_color(*BORDER)
        pdf.rect(x, y, img_w, img_w)
        pdf.set_xy(x, y + img_w + 1.5)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*INK_SOFT)
        pdf.cell(img_w, 4.5, caption, align="C")
    y += img_w + 7

    # legend + affected share
    pdf.set_xy(MARGIN, y)
    pdf.set_font("Helvetica", "", 7.8)
    pdf.set_text_color(*MUTED)
    note = "Heatmap: red and yellow areas mattered most for the answer."
    if not healthy and affected_percent is not None:
        note += f" The red outline covers about {affected_percent:.0f}% of the photo (AI estimate, not a measurement)."
    pdf.multi_cell(CONTENT_W, 3.8, note, new_x="LMARGIN", new_y="NEXT")
    y = pdf.get_y() + 3

    # ── About ────────────────────────────────────────────────────────────
    desc = disease_info.get("description")
    if desc:
        _heading(pdf, "About this result" if healthy else f"About {pred}", y)
        pdf.set_font("Helvetica", "", 8.8)
        pdf.set_text_color(*INK)
        pdf.multi_cell(CONTENT_W, 4.4, _clean(desc), new_x="LMARGIN", new_y="NEXT")
        y = pdf.get_y() + 3

    # ── Signs + treatment (two columns) ─────────────────────────────────
    col_w = (CONTENT_W - 8) / 2
    _heading(pdf, "What a healthy mango looks like" if healthy else "Signs to check", y, MARGIN, col_w)
    y_left = _bullets(pdf, disease_info.get("symptoms", []), MARGIN, y + 7, col_w)
    _heading(pdf, "What to do now" if not healthy else "Keep it healthy", y, MARGIN + col_w + 8, col_w)
    y_right = _bullets(pdf, disease_info.get("remedies", []), MARGIN + col_w + 8, y + 7, col_w, numbered=True)
    y = max(y_left, y_right) + 3

    # ── All scores (compact bars, two columns) ───────────────────────────
    scores = classification.get("all_scores", [])
    if scores:
        _heading(pdf, "How sure the AI is for each class", y)
        y += 7
        half = (CONTENT_W - 8) / 2
        name_w, pct_w = 34, 14
        bar_w = half - name_w - pct_w - 2
        for i, s in enumerate(scores):
            col, row = divmod(i, 4)
            x = MARGIN + col * (half + 8)
            yy = y + row * 6
            top = i == 0
            pdf.set_xy(x, yy)
            pdf.set_font("Helvetica", "B" if top else "", 8.5)
            pdf.set_text_color(*INK)
            pdf.cell(name_w, 4.5, _clean(s["class"]))
            pdf.set_fill_color(*GREEN_TINT)
            pdf.rect(x + name_w, yy + 1, bar_w, 2.6, style="F", round_corners=True, corner_radius=1.3)
            fill = max(0.8, bar_w * float(s["score"]))
            pdf.set_fill_color(*(tone if top else (156, 204, 101)))
            # Rounded corners only when the bar is wider than its height (tiny bars glitch otherwise)
            if fill > 2.6:
                pdf.rect(x + name_w, yy + 1, fill, 2.6, style="F", round_corners=True, corner_radius=1.3)
            else:
                pdf.rect(x + name_w, yy + 1, fill, 2.6, style="F")
            pdf.set_xy(x + name_w + bar_w + 1, yy)
            pdf.cell(pct_w, 4.5, f"{float(s['score']) * 100:.1f}%", align="R")

    return bytes(pdf.output())
