"""
mango-disease-ai - Python quick start
=====================================
Analyze one mango photo, print the diagnosis and save the Grad-CAM++ heatmap and
a PDF report.

    pip install mango-disease-ai
    python examples/quick_start.py                      # uses examples/sample_mango.jpg
    python examples/quick_start.py path/to/mango.jpg    # your own photo

The first run downloads the CLIP mango checker (about 600 MB) once.
"""
import base64
import sys
from pathlib import Path

from mango_disease_ai import analyze, generate_pdf

image_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("sample_mango.jpg")

# 1. Analyze: CLIP mango check -> AA-ENet classification -> Grad-CAM++ heatmap
result = analyze(str(image_path))

if not result["is_mango"]:
    print(f"Not a mango photo (mango confidence {result['mango_confidence']:.1%})")
    sys.exit(1)

# 2. Prediction and probabilities of all 7 classes
print(f"Image      : {image_path}")
print(f"Disease    : {result['predicted_class']}")
print(f"Confidence : {result['confidence']:.2%}\n")
print("All class probabilities:")
for item in result["all_scores"]:
    print(f"  {item['class']:<18} {item['score']:.4f}")

# 3. Disease guidance
info = result["disease_info"]
print(f"\nScientific name: {info['scientific_name']}")
print("Remedies:")
for step in info["remedies"]:
    print(f"  - {step}")

# 4. Save the Grad-CAM++ heatmap and the PDF report
Path("gradcam_heatmap.jpg").write_bytes(base64.b64decode(result["gradcam_base64"]))
Path("mango_report.pdf").write_bytes(generate_pdf(result, user_name="Researcher"))
print("\nSaved: gradcam_heatmap.jpg, mango_report.pdf")
