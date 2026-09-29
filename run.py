"""
Start AmropaliNet with one click (VS Code ▶ Run) or: python run.py
Opens http://localhost:8000 in your browser.
"""

import os
import threading
import webbrowser

# PyTorch only: keep transformers from importing TensorFlow/Keras if installed
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

import uvicorn

PORT = 8000

if __name__ == "__main__":
    threading.Timer(2.0, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
    uvicorn.run("api.main:app", host="127.0.0.1", port=PORT)
