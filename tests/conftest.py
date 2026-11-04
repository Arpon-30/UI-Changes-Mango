"""Shared fixtures. The tests never download the CLIP model, so they run offline and fast."""
import base64
import io

import pytest
from PIL import Image


def _jpeg_b64(color, size=(224, 224)) -> str:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


@pytest.fixture
def sample_image() -> Image.Image:
    """A small synthetic RGB image (mango-like yellow)."""
    return Image.new("RGB", (300, 260), (230, 190, 60))


@pytest.fixture
def fake_result() -> dict:
    """A result dict shaped like the output of analyze(), for report tests."""
    from mango_disease_ai.model import CLASSES, DISEASE_INFO

    scores = [0.91, 0.03, 0.02, 0.015, 0.012, 0.008, 0.005]
    return {
        "is_mango": True,
        "mango_confidence": 0.97,
        "predicted_class": CLASSES[0],
        "confidence": scores[0],
        "all_scores": [{"class": c, "score": s} for c, s in zip(CLASSES, scores)],
        "disease_info": DISEASE_INFO[CLASSES[0]],
        "original_base64": _jpeg_b64((230, 190, 60)),
        "gradcam_base64": _jpeg_b64((200, 60, 40)),
        "marked_base64": None,
        "affected_percent": None,
    }
