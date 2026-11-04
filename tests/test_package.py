"""Package metadata, public API and disease information."""
import mango_disease_ai
from mango_disease_ai.model import CLASSES, DISEASE_INFO, NUM_CLASSES

EXPECTED_CLASSES = [
    "Anthracnose",
    "Bacterial Canker",
    "Healthy",
    "Powdery Mildew",
    "Scab",
    "Sooty Mould",
    "Stem End Rot",
]


def test_public_api():
    assert callable(mango_disease_ai.analyze)
    assert callable(mango_disease_ai.generate_pdf)
    assert isinstance(mango_disease_ai.__version__, str)


def test_classes():
    assert CLASSES == EXPECTED_CLASSES
    assert NUM_CLASSES == 7


def test_disease_info_complete():
    for name in CLASSES:
        info = DISEASE_INFO[name]
        for key in ("scientific_name", "description", "symptoms", "remedies"):
            assert info.get(key), f"{name}: missing {key}"
