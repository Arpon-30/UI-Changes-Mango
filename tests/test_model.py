"""The bundled AA-ENet weights load and the model produces valid class probabilities."""
import os

import pytest
import torch

from mango_disease_ai.model import CLASSES, IMG_SIZE, MODEL_PATH, load_model


def test_weights_bundled():
    assert os.path.exists(MODEL_PATH)
    # Real weights (~18 MB), not a Git LFS pointer file
    assert os.path.getsize(MODEL_PATH) > 10 * 1024 * 1024


def test_forward_pass():
    model = load_model()
    with torch.no_grad():
        logits = model(torch.rand(2, 3, IMG_SIZE, IMG_SIZE))
    assert logits.shape == (2, len(CLASSES))
    probs = torch.softmax(logits, dim=1)
    assert torch.allclose(probs.sum(dim=1), torch.ones(2), atol=1e-5)


def test_parameter_count():
    model = load_model()
    n_params = sum(p.numel() for p in model.parameters())
    # Lightweight model for CPU deployment
    assert 3e6 < n_params < 8e6


def test_classify_image(sample_image):
    from mango_disease_ai.inference import classify_image

    out = classify_image(sample_image)
    assert out["predicted_class"] in CLASSES
    assert 0.0 <= out["confidence"] <= 1.0
    assert len(out["all_scores"]) == len(CLASSES)
    assert sum(s["score"] for s in out["all_scores"]) == pytest.approx(1.0, abs=1e-3)


def test_gradcam(sample_image):
    from mango_disease_ai.inference import generate_gradcam

    out = generate_gradcam(sample_image)
    assert out  # heatmap images are produced
