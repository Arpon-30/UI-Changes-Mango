"""
AmropaliNet - Streamlit version (for free hosting on Streamlit Community Cloud).

Same AI and features as the website, from the same library (mango_disease_ai):
mango check, 7-class diagnosis, Grad-CAM + marked affected area, advice, Bangla or
English PDF, Bangla / English interface, phone camera.

Runs in low-memory mode (MANGO_LOW_MEMORY=1) so it fits the ~1 GB free tier.

    streamlit run streamlit_app.py
"""

from __future__ import annotations

import os

# Must be set before the library is imported
os.environ.setdefault("MANGO_LOW_MEMORY", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

import base64
import hashlib
import html
import io
import json
from pathlib import Path

import streamlit as st
from PIL import Image

ROOT = Path(__file__).resolve().parent
TEXT = json.loads((ROOT / "static" / "data" / "ui_text.json").read_text(encoding="utf-8"))
DISEASES = json.loads((ROOT / "static" / "data" / "diseases.json").read_text(encoding="utf-8"))
BY_KEY = {d["key"]: d for d in DISEASES}
BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

EXTRA = {
    "en": {"lang": "Language", "tab_cam": "📷 Take photo", "tab_up": "🖼️ Upload a photo",
           "no_photo": "Take or upload a photo first.", "loading": "Getting the AI ready (first time can take a minute)...",
           "encyclopedia": "Disease Encyclopedia", "sdg": "UN Sustainable Development Goals"},
    "bn": {"lang": "ভাষা", "tab_cam": "📷 ছবি তুলুন", "tab_up": "🖼️ ছবি আপলোড",
           "no_photo": "আগে একটি ছবি তুলুন বা আপলোড করুন।", "loading": "এআই প্রস্তুত হচ্ছে (প্রথমবার এক মিনিট লাগতে পারে)...",
           "encyclopedia": "রোগ বিশ্বকোষ", "sdg": "জাতিসংঘের টেকসই উন্নয়ন লক্ষ্য"},
}

st.set_page_config(page_title="AmropaliNet - Mango Disease Doctor", page_icon="🥭", layout="centered")

# ── Language ─────────────────────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "bn"


def lang() -> str:
    return st.session_state.lang


def t(key: str) -> str:
    return EXTRA[lang()].get(key) or TEXT[lang()].get(key) or TEXT["en"].get(key) or key


def L(obj):
    """Pick the current language from {"en": ..., "bn": ...}."""
    if isinstance(obj, dict):
        return obj.get(lang()) or obj.get("en")
    return obj


def num(x) -> str:
    return str(x).translate(BN_DIGITS) if lang() == "bn" else str(x)


def pct(x: float, dp: int = 1) -> str:
    return num(f"{x * 100:.{dp}f}") + "%"


def esc(s) -> str:
    return html.escape(str(s))


# ── Style (orchard palette, Bangla font) ─────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;600;700&family=Poppins:wght@400;600;800&display=swap');
html, body, [class*="css"], .stApp, .stMarkdown, button, input, label { font-family: "Hind Siliguri", "Poppins", sans-serif !important; }
.stApp { background: linear-gradient(180deg, #F8FBF1 0%, #EEF6E3 100%); }
.block-container { padding-top: 3.6rem; max-width: 820px; }  /* keep content below Streamlit's top bar */
.ticker { background: linear-gradient(90deg,#1B5E20,#2E7D32); color:#F1FAE6; padding:8px 14px; border-radius:12px; font-size:.9rem; margin-bottom:12px; }
.brand { font-family:"Poppins",sans-serif; font-weight:800; font-size:1.7rem; color:#1D3A1F; margin:0; }
.brand span { color:#FB8C00; }
.badge { display:inline-block; padding:6px 12px; border-radius:999px; background:#fff; border:1px solid #DCEBCD; color:#2E7D32; font-weight:600; font-size:.85rem; }
.hero-title { font-size:2.2rem; font-weight:800; line-height:1.15; color:#1D3A1F; margin:.4rem 0 .2rem; }
.hero-title b { background:linear-gradient(90deg,#2E7D32,#FB8C00); -webkit-background-clip:text; background-clip:text; color:transparent; }
.muted { color:#4E6B4A; }
.card { background:#fff; border:1px solid #DCEBCD; border-radius:18px; padding:18px 20px; box-shadow:0 4px 14px rgba(29,58,31,.07); margin:10px 0; }
.verdict { border-left:8px solid var(--tone,#2E7D32); }
.verdict h3 { margin:.1rem 0; font-size:1.6rem; color:#1D3A1F; }
.verdict h3 em { font-style:normal; color:var(--tone,#2E7D32); }
.sci { font-style:italic; color:#6B8466; }
.pill { display:inline-block; padding:3px 10px; border-radius:999px; font-size:.8rem; font-weight:600; margin:2px 4px 2px 0; background:#F1F7E8; color:#4E6B4A; }
.pill.high { background:#FDECEA; color:#C62828; } .pill.medium { background:#FFF4DB; color:#7A4A00; } .pill.none { background:#E3F2D3; color:#1B5E20; }
.big { font-size:2rem; font-weight:800; color:#1D3A1F; }
.warn { background:#FFF4DB; color:#7A4A00; border-radius:12px; padding:10px 14px; }
.bad { background:#FDECEA; color:#C62828; border-radius:12px; padding:10px 14px; font-weight:600; }
.good { background:#E3F2D3; color:#1B5E20; border-radius:12px; padding:10px 14px; font-weight:600; }
.bar { height:9px; border-radius:9px; background:#F1F7E8; overflow:hidden; margin:2px 0 8px; }
.bar i { display:block; height:100%; border-radius:9px; background:#9CCC65; }
.bar.top i { background:linear-gradient(90deg,#388E3C,#FFB300); }
.sdg { display:inline-block; color:#fff; font-weight:700; border-radius:10px; padding:4px 10px; margin-right:8px; }
.foot { background:#1F4D24; color:#E8F5E0; border-radius:18px; padding:18px 20px; margin-top:24px; font-size:.92rem; }
.foot a { color:#FFD54F; }
div.stButton > button, div.stDownloadButton > button { border-radius:999px; font-weight:700; min-height:48px; }
div.stButton > button[kind="primary"] { background:linear-gradient(135deg,#2E7D32,#43A047); border:0; }
</style>
""",
    unsafe_allow_html=True,
)


# ── AI (cached) ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def warm_up() -> bool:
    from mango_disease_ai.model import load_mango_detector, load_model

    load_model()
    load_mango_detector()
    return True


@st.cache_data(show_spinner=False, max_entries=6)
def run_analysis(image_bytes: bytes) -> dict:
    from mango_disease_ai import analyze

    return analyze(image_bytes, include_gradcam=True)


@st.cache_data(show_spinner=False, max_entries=12)
def make_pdf(digest: str, image_bytes: bytes, name: str, pdf_lang: str) -> bytes:
    from mango_disease_ai import generate_pdf

    return generate_pdf(run_analysis(image_bytes), user_name=name, lang=pdf_lang)


def b64_image(b64: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(b64)))


# ── Header ───────────────────────────────────────────────────────────────────
top_l, top_r = st.columns([3, 2])
with top_l:
    st.markdown('<p class="brand">🥭 Amropali<span>Net</span></p>', unsafe_allow_html=True)
with top_r:
    # A callback (not st.rerun mid-script) so the photo widgets below keep their value
    def _set_lang():
        st.session_state.lang = "bn" if st.session_state.lang_choice == "বাংলা" else "en"

    if "lang_choice" not in st.session_state:
        st.session_state.lang_choice = "বাংলা" if lang() == "bn" else "English"
    st.radio("Language / ভাষা", ["বাংলা", "English"], horizontal=True,
             label_visibility="collapsed", key="lang_choice", on_change=_set_lang)

st.markdown(f'<div class="ticker">{esc(t("ticker.1"))}<br>{esc(t("ticker.2"))}</div>', unsafe_allow_html=True)
st.markdown(
    f'<span class="badge">{esc(t("hero.badge"))}</span>'
    f'<div class="hero-title">{esc(t("hero.title1"))} <b>{esc(t("hero.title2"))}</b></div>'
    f'<p class="muted">{esc(t("hero.sub"))}</p>',
    unsafe_allow_html=True,
)

# ── Scan ─────────────────────────────────────────────────────────────────────
st.subheader(t("detect.title"))
st.caption(t("detect.sub"))


def _photo_changed():
    # The farmer took or removed a photo: forget the previous result
    st.session_state.pop("checked", None)
    st.session_state.pop("checked_bytes", None)


tab_cam, tab_up = st.tabs([t("tab_cam"), t("tab_up")])
with tab_cam:
    # Fixed (language-independent) labels + keys: a changing label would reset the widget
    cam = st.camera_input("Camera / ক্যামেরা", label_visibility="collapsed", key="camera", on_change=_photo_changed)
with tab_up:
    up = st.file_uploader("Photo / ছবি", type=["jpg", "jpeg", "png", "webp", "bmp", "tif", "tiff"],
                          label_visibility="collapsed", key="upload",
                          on_change=_photo_changed)
    st.caption(t("detect.hint"))

photo = cam or up
image_bytes = None
if photo is not None:
    raw = photo.getvalue()
    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        img.thumbnail((1600, 1600))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=90)
        image_bytes = buf.getvalue()
    except Exception:
        st.markdown(f'<div class="bad">{esc(t("err.bad"))}</div>', unsafe_allow_html=True)

if st.button(t("detect.check"), type="primary", use_container_width=True, disabled=image_bytes is None):
    st.session_state.checked = hashlib.sha1(image_bytes).hexdigest()
    st.session_state.checked_bytes = image_bytes

# Keep the checked photo across reruns (for example a language switch), even if a
# photo widget is re-created and briefly reports no file.
if image_bytes is None and st.session_state.get("checked_bytes"):
    image_bytes = st.session_state.checked_bytes

digest = hashlib.sha1(image_bytes).hexdigest() if image_bytes else None
show = digest is not None and st.session_state.get("checked") == digest

# ── Result ───────────────────────────────────────────────────────────────────
if show:
    try:
        with st.spinner(t("loading")):
            warm_up()
        with st.spinner(t("detect.loading1")):
            result = run_analysis(image_bytes)
    except Exception as exc:  # model file / CLIP download problems
        st.error(f"{t('err.server')}\n\n{exc}")
        st.stop()

    if not result["is_mango"]:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(image_bytes, use_container_width=True)
        with c2:
            st.markdown(
                f'<div class="card" style="border-left:8px solid #C62828"><h3 style="color:#C62828;margin:0">{esc(t("nm.title"))}</h3>'
                f'<p class="muted">{esc(t("nm.sub").replace("{pct}", pct(result["mango_confidence"], 0)))}</p>'
                f'<ul><li>{esc(t("nm.t1"))}</li><li>{esc(t("nm.t2"))}</li><li>{esc(t("nm.t3"))}</li></ul></div>',
                unsafe_allow_html=True,
            )
        st.stop()

    d = BY_KEY.get(result["predicted_class"], BY_KEY["Healthy"])
    healthy = d["key"] == "Healthy"
    conf = float(result["confidence"])
    tone = "#2E7D32" if healthy else "#E65100"
    title = f'{esc(t("res.healthy"))} 🌿' if healthy else f'{esc(t("res.sick"))} <em>{esc(L(d["name"]))}</em>'
    parts = "".join(f'<span class="pill">{esc(t("part." + p))}</span>' for p in d["parts"])
    st.markdown(
        f'<div class="card verdict" style="--tone:{tone}">'
        f'<div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap">'
        f'<div><span class="muted" style="font-size:.8rem;font-weight:700;color:#FB8C00">{esc(t("res.kicker"))}</span>'
        f'<h3>{title}</h3><div class="sci">{esc(d["sci"])}</div>'
        f'<span class="pill {d["risk"]}">{esc(t("res.risk"))}: {esc(t("risk." + d["risk"]))}</span>{parts}</div>'
        f'<div style="text-align:right"><div class="big">{pct(conf, 0)}</div><div class="muted">{esc(t("res.sure"))}</div></div>'
        f"</div></div>",
        unsafe_allow_html=True,
    )
    if conf < 0.7:
        st.markdown(f'<div class="warn">{esc(t("res.lowconf"))}</div>', unsafe_allow_html=True)

    # Heatmap + marked area
    st.markdown(f"#### 🔥 {t('res.heattitle')}")
    cols = st.columns(3 if (result.get("marked_base64") and not healthy) else 2)
    cols[0].image(b64_image(result["original_base64"]), caption=t("res.photo"), use_container_width=True)
    cols[1].image(b64_image(result["gradcam_base64"]), caption=t("res.heat"), use_container_width=True)
    if len(cols) == 3:
        cols[2].image(b64_image(result["marked_base64"]), caption=t("res.marked"), use_container_width=True)
    if healthy:
        st.markdown(f'<div class="good">{esc(t("res.noaffected"))}</div>', unsafe_allow_html=True)
    elif result.get("affected_percent") is not None:
        msg = t("res.affected").replace("{pct}", num(round(result["affected_percent"])) + "%")
        st.markdown(f'<div class="bad">{esc(msg)}</div>', unsafe_allow_html=True)
    st.caption(t("res.heatnote"))

    # Advice
    a1, a2 = st.columns(2)
    with a1:
        st.markdown(f"#### ✅ {t('res.todo')}")
        st.markdown("\n".join(f"{num(i)}. {r}" for i, r in enumerate(L(d["remedies"]), 1)))
    with a2:
        st.markdown(f"#### 👀 {t('res.signs')}")
        st.markdown("\n".join(f"- {s}" for s in L(d["symptoms"])))

    # All scores
    with st.expander(f"📊 {t('res.scores')}"):
        rows = []
        for i, s in enumerate(result["all_scores"]):
            name = L(BY_KEY[s["class"]]["name"]) if s["class"] in BY_KEY else s["class"]
            rows.append(f'<div style="display:flex;justify-content:space-between"><span>{esc(name)}</span><b>{pct(s["score"])}</b></div>'
                        f'<div class="bar {"top" if i == 0 else ""}"><i style="width:{s["score"] * 100:.1f}%"></i></div>')
        st.markdown("".join(rows), unsafe_allow_html=True)

    # Garden impact
    with st.expander(f"🌳 {t('garden.title')}"):
        st.markdown(f"**{t('garden.spread')}:** {L(d['spread'])}")
        st.markdown(f"**{t('garden.season')}:** {num(L(d['season']))}")
        st.markdown(f"**{t('dis.prevent')}:**\n" + "\n".join(f"- {p}" for p in L(d["prevent"])))

    # PDF report
    st.markdown(f"#### 📄 {t('rep.title')}")
    st.caption(t("rep.sub"))
    st.markdown(f"**{t('rep.name')}**")
    name = st.text_input("Name / নাম", placeholder="Name / নাম", label_visibility="collapsed", key="report_name").strip()
    if name:
        st.caption(t("rep.choose"))
        p1, p2 = st.columns(2)
        safe = "".join(c if c.isascii() and c.isalnum() else "_" for c in name).strip("_") or "report"
        for col, pdf_lang, label in ((p1, "bn", t("rep.bn")), (p2, "en", t("rep.en"))):
            try:
                data = make_pdf(digest, image_bytes, name, pdf_lang)
                col.download_button(f"⬇️ {label}", data=data, file_name=f"AmropaliNet_Report_{safe}_{pdf_lang.upper()}.pdf",
                                    mime="application/pdf", use_container_width=True)
            except Exception as exc:
                col.error(f"{t('err.bnpdf') if pdf_lang == 'bn' else t('err.server')}\n\n{exc}")
    else:
        st.caption(t("rep.err"))

# ── Encyclopedia ─────────────────────────────────────────────────────────────
st.divider()
st.subheader(f"📚 {t('encyclopedia')}")
st.caption(t("dis.sub"))
for d in DISEASES:
    with st.expander(f"{d['emoji']}  {L(d['name'])}  ·  {t('risk.' + d['risk'])}"):
        c1, c2 = st.columns([1, 2])
        photo_path = ROOT / "static" / "img" / "diseases" / (d["key"].lower().replace(" ", "-") + ".jpg")
        if photo_path.exists():
            c1.image(str(photo_path), use_container_width=True)
        c2.markdown(f"*{d['sci']}*\n\n{L(d['desc'])}")
        st.markdown(f"**👀 {t('dis.symptoms')}**\n" + "\n".join(f"- {s}" for s in L(d["symptoms"])))
        st.markdown(f"**✅ {t('dis.treatment')}**\n" + "\n".join(f"{num(i)}. {r}" for i, r in enumerate(L(d["remedies"]), 1)))
        st.markdown(f"**🌬️ {t('dis.spread')}:** {L(d['spread'])}")

# ── Environment + SDGs ───────────────────────────────────────────────────────
st.divider()
st.subheader(f"🌱 {t('env.title')}")
st.caption(t("env.sub"))
e1, e2 = st.columns(2)
for i, (icon, key) in enumerate((("🎯", "c1"), ("🥭", "c2"), ("🐝", "c3"), ("👨‍🌾", "c4"))):
    (e1 if i % 2 == 0 else e2).markdown(
        f'<div class="card"><b>{icon} {esc(t("env." + key + "t"))}</b><br><span class="muted">{esc(t("env." + key + "d"))}</span></div>',
        unsafe_allow_html=True)
st.markdown(f"**{t('sdg')}**")
for n, color in ((1, "#E5243B"), (2, "#DDA63A"), (12, "#BF8B2E"), (13, "#3F7E44"), (15, "#56C02B")):
    st.markdown(f'<div style="margin:6px 0"><span class="sdg" style="background:{color}">SDG {num(n)}</span>'
                f'<b>{esc(t(f"env.sdg{n}"))}</b> - <span class="muted">{esc(t(f"env.sdg{n}d"))}</span></div>',
                unsafe_allow_html=True)

# ── Developers ───────────────────────────────────────────────────────────────
st.divider()
st.subheader(f"👩‍💻 {t('dev.title')}")
st.caption(t("dev.sub"))
d1, d2, d3 = st.tabs(["Python", "REST API", "JavaScript"])
d1.code('''pip install mango-disease-ai

from mango_disease_ai import analyze, generate_pdf

result = analyze("mango.jpg")
if result["is_mango"]:
    print(result["predicted_class"], result["confidence"])
    pdf = generate_pdf(result, user_name="Arpon", lang="bn")
    open("report.pdf", "wb").write(pdf)''', language="python")
d2.code('''pip install "mango-disease-ai[api]"
mango-api            # http://localhost:8000/docs

curl -F "image=@mango.jpg" http://localhost:8000/api/analyze''', language="bash")
d3.code('''const form = new FormData();
form.append("image", fileInput.files[0]);
const res = await fetch("http://localhost:8000/api/analyze", { method: "POST", body: form });
const data = await res.json();''', language="javascript")
st.markdown("[📦 PyPI: mango-disease-ai](https://pypi.org/project/mango-disease-ai/)")

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="foot"><b style="font-size:1.1rem">AmropaliNet</b> - {esc(t("foot.tag"))}<br><br>'
    f'<b>{esc(t("foot.group"))}</b>: Arpon, Oni, Md. Ibtihazzaman<br>'
    f'{esc(t("foot.sup"))} Dr. Md. Saef Ullah Miah<br>'
    f'✉️ <a href="mailto:arponamit.55@gmail.com">arponamit.55@gmail.com</a> · '
    f'<a href="https://github.com/Arpon-30" target="_blank">github.com/Arpon-30</a><br><br>'
    f'<span style="opacity:.85">{esc(t("foot.disc"))}</span></div>',
    unsafe_allow_html=True,
)
