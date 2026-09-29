# mango-disease-ai 🥭

> AI-powered Amropali mango disease detection — classify 7 diseases, visualize with Grad-CAM, and generate PDF reports.

[![PyPI version](https://badge.fury.io/py/mango-disease-ai.svg)](https://badge.fury.io/py/mango-disease-ai)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## What It Does

`mango-disease-ai` is a Python package built on the **AA-ENet** model — a lightweight CNN–Transformer hybrid developed by the **AIUB R&D ICCA Research Group** — that detects 7 Amropali mango diseases from images.

| Feature | Description |
|---------|-------------|
| 🔍 **Disease Classification** | Detects 7 diseases with confidence scores |
| 🧠 **Mango Validation** | Auto-rejects non-mango images using CLIP |
| 🌡️ **Grad-CAM Heatmap** | Shows exactly where the AI focused on the image |
| 📄 **PDF Report** | Generates a professional diagnosis report |
| 🌐 **Public REST API** | Callable from mobile apps, web apps, Postman |

### Detectable Diseases

1. **Anthracnose** — *Colletotrichum gloeosporioides*
2. **Bacterial Canker** — *Xanthomonas campestris pv. mangiferaeindicae*
3. **Healthy** — No disease detected
4. **Powdery Mildew** — *Oidium mangiferae*
5. **Scab** — *Elsinoë mangiferae*
6. **Sooty Mould** — *Capnodium mangiferae*
7. **Stem End Rot** — *Lasiodiplodia theobromae*

---

## Installation

```bash
pip install mango-disease-ai
```

> **Note:** The first run will automatically download the CLIP model (~600 MB) from HuggingFace Hub. Subsequent runs use the cached version.

---

## Quick Start

### Analyze an image

```python
from mango_disease_ai import analyze

# Works with file path, PIL Image, bytes, or file-like objects
result = analyze("mango_leaf.jpg")

print(result["predicted_class"])    # e.g. "Anthracnose"
print(result["confidence"])         # e.g. 0.9312  (93.12%)
print(result["is_mango"])           # True

# Disease details
info = result["disease_info"]
print(info["scientific_name"])      # "Colletotrichum gloeosporioides"
print(info["symptoms"])             # list of symptom strings
print(info["remedies"])             # list of treatment strings

# All 7 class scores
for score in result["all_scores"]:
    print(f"{score['class']:20s} {score['score']:.4f}")
```

### Generate a PDF report

```python
from mango_disease_ai import analyze, generate_pdf

result = analyze("mango_leaf.jpg")

pdf_bytes = generate_pdf(result, user_name="Dr. Arpon")
with open("diagnosis_report.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### Display the Grad-CAM heatmap

```python
import base64
from mango_disease_ai import analyze

result = analyze("mango_leaf.jpg")

# Decode the Grad-CAM base64 PNG and save
heatmap_bytes = base64.b64decode(result["gradcam_base64"])
with open("heatmap.png", "wb") as f:
    f.write(heatmap_bytes)
```

### Fast mode (no Grad-CAM — ~2× faster)

```python
from mango_disease_ai import analyze

result = analyze("mango_leaf.jpg", include_gradcam=False)
# gradcam_base64 and original_base64 will be None
```

### Works with PIL Images

```python
from PIL import Image
from mango_disease_ai import analyze

pil_img = Image.open("mango.jpg")
result = analyze(pil_img)
```

---

## Return Value

`analyze()` returns a dictionary:

```python
{
    "is_mango": True,               # bool — was it validated as a mango?
    "mango_confidence": 0.97,       # float — CLIP mango detection score
    "predicted_class": "Anthracnose",
    "confidence": 0.9312,           # top class confidence (0.0–1.0)
    "all_scores": [
        {"class": "Anthracnose", "score": 0.9312},
        {"class": "Healthy",     "score": 0.0412},
        # ... all 7 classes
    ],
    "disease_info": {
        "scientific_name": "Colletotrichum gloeosporioides",
        "description": "...",
        "symptoms": ["Dark brown spots...", ...],
        "remedies":  ["Apply copper-based fungicides...", ...]
    },
    "gradcam_base64": "iVBORw0KGgo...",   # base64 PNG string
    "original_base64": "iVBORw0KGgo...",  # base64 PNG string
}
```

If `is_mango` is `False`, all other fields except `mango_confidence` will be `None` or empty.

---

## Public REST API

A public internet API is also available at **Hugging Face Spaces**.
Any mobile app or web app can call it via HTTP — no Python needed.

### Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/health` | Server health check |
| GET | `/api/diseases` | List all 7 diseases |
| POST | `/api/analyze` | Analyze image → JSON result |
| POST | `/api/report` | Analyze image → PDF download |

### Example (Python requests)

```python
import requests

with open("mango_leaf.jpg", "rb") as f:
    response = requests.post(
        "https://YOUR-SPACE.hf.space/api/analyze",
        files={"image": f},
    )

result = response.json()
print(result["predicted_class"])
print(result["confidence"])
```

### Example (curl)

```bash
curl -X POST "https://YOUR-SPACE.hf.space/api/analyze" \
     -F "image=@mango_leaf.jpg"
```

### Interactive API Docs

Visit `https://YOUR-SPACE.hf.space/docs` for the full interactive documentation (Swagger UI).

---

## Model Architecture

**AA-ENet** (Amropali Attention-Enhanced Network):

```
Input Image (224×224)
       │
EfficientNet-B0 Backbone (pretrained)
       │
1×1 Conv Reduction → 192 channels
       │
CBAM Attention (Channel + Spatial)
       │
Transformer Encoder (1 layer, 4 heads) + [CLS] token
       │
GAP + CLS concatenation → Dropout → Linear
       │
7-class softmax output
```

- **Parameters**: ~5.8M
- **Training data**: 3,500 Amropali mango images (500 per class)
- **Inference time**: ~1–2 seconds (CPU)
- **Input**: 224×224, ImageNet normalization

---

## License

MIT License — see [LICENSE](LICENSE) file.

## Attribution

**Research Group**: AIUB R&D ICCA  
**Institution**: American International University-Bangladesh  
**Model**: AA-ENet (EfficientNet-B0 + CBAM + Transformer Encoder)  
**Dataset**: 3,500 Amropali mango images

If you use this in research, please cite our work.
