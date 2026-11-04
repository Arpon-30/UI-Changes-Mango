"""
mango-disease-ai - REST API client example
==========================================
Start the server first (in another terminal):

    pip install "mango-disease-ai[api]" requests
    mango-api                                  # http://localhost:8000, docs at /docs

Then run:

    python examples/rest_api_client.py                      # uses examples/sample_mango.jpg
    python examples/rest_api_client.py path/to/mango.jpg
"""
import sys
from pathlib import Path

import requests

API = "http://localhost:8000"
image_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("sample_mango.jpg")

# Health check
print("Health:", requests.get(f"{API}/api/health", timeout=10).json())

# Diagnosis as JSON
with open(image_path, "rb") as f:
    r = requests.post(f"{API}/api/analyze", files={"image": (image_path.name, f, "image/jpeg")}, timeout=300)
if r.status_code == 422:
    print("Not a mango photo:", r.json()["detail"])
    sys.exit(1)
r.raise_for_status()
result = r.json()
print(f"Disease: {result['predicted_class']} ({result['confidence']:.2%})")

# PDF report
with open(image_path, "rb") as f:
    r = requests.post(
        f"{API}/api/report",
        files={"image": (image_path.name, f, "image/jpeg")},
        data={"user_name": "Researcher", "lang": "en"},
        timeout=300,
    )
r.raise_for_status()
Path("mango_report.pdf").write_bytes(r.content)
print("Saved: mango_report.pdf")
