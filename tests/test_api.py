"""REST API endpoints (no model download needed)."""
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient

from mango_disease_ai.server import create_app

# Not used as a context manager, so the background model warm-up (CLIP download) does not start.
client = TestClient(create_app())


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_diseases():
    r = client.get("/api/diseases")
    assert r.status_code == 200
    assert len(r.json()["diseases"]) == 7


def test_openapi_docs():
    assert client.get("/docs").status_code == 200
    paths = client.get("/openapi.json").json()["paths"]
    for path in ("/api/health", "/api/diseases", "/api/analyze", "/api/report"):
        assert path in paths


def test_analyze_requires_image():
    assert client.post("/api/analyze").status_code == 422


def test_analyze_rejects_wrong_file_type():
    r = client.post("/api/analyze", files={"image": ("notes.txt", b"hello", "text/plain")})
    assert r.status_code == 400


def test_report_requires_name():
    r = client.post(
        "/api/report",
        files={"image": ("m.jpg", b"x", "image/jpeg")},
        data={"user_name": "   "},
    )
    assert r.status_code == 400
