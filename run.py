"""
Start AmropaliNet with one click (VS Code ▶ Run) or: python run.py
Opens http://localhost:8000 in your browser.
"""

import threading
import webbrowser

import uvicorn

PORT = 8000

if __name__ == "__main__":
    threading.Timer(2.0, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
    uvicorn.run("api.main:app", host="127.0.0.1", port=PORT)
