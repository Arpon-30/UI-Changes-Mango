"""PDF report generation."""
import pytest

from mango_disease_ai import generate_pdf


def test_pdf_english(fake_result):
    pdf = generate_pdf(fake_result, user_name="Test User")
    assert pdf[:5] == b"%PDF-"
    assert len(pdf) > 1000


def test_pdf_rejects_non_mango(fake_result):
    fake_result["is_mango"] = False
    with pytest.raises(ValueError):
        generate_pdf(fake_result, user_name="Test User")


def test_pdf_bangla(fake_result):
    pytest.importorskip("uharfbuzz")
    pdf = generate_pdf(fake_result, user_name="Test User", lang="bn")
    assert pdf[:5] == b"%PDF-"
