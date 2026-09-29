"""
Background photos for the website (real mango gardens, a Bangladeshi farmer, harvest).

The photos are free Unsplash images (Unsplash License: free to use, no attribution
required). They are downloaded once into static/img/photos/ when the server starts,
so the repository stays small. To use your own photos, put JPG files with the same
names in that folder - existing files are never overwritten.
"""

from __future__ import annotations

import io
import logging
import urllib.request
from pathlib import Path

log = logging.getLogger("amropalinet")

PHOTO_DIR = Path(__file__).resolve().parent.parent / "static" / "img" / "photos"

# file name -> Unsplash photo id
PHOTOS = {
    "hero.jpg": "vJE_YCb92Wg",     # mango tree with green mangoes
    "branch.jpg": "RnbBIt2WoJw",   # green and ripe mango on a branch
    "farmer.jpg": "oTtL2Z-4i1s",   # farmer in a field, Chilmari, Bangladesh
    "harvest.jpg": "7DrqdqKTroY",  # pile of ripe mangoes
}
MAX_WIDTH = 1800


def ensure_photos() -> None:
    """Download any missing photo. Safe to call on every start; failures are only logged."""
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    for name, photo_id in PHOTOS.items():
        target = PHOTO_DIR / name
        if target.exists() and target.stat().st_size > 10_000:
            continue
        url = f"https://unsplash.com/photos/{photo_id}/download?force=true"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AmropaliNet/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            from PIL import Image

            img = Image.open(io.BytesIO(data)).convert("RGB")
            if img.width > MAX_WIDTH:
                img = img.resize((MAX_WIDTH, round(img.height * MAX_WIDTH / img.width)), Image.LANCZOS)
            img.save(target, "JPEG", quality=82, optimize=True, progressive=True)
            log.info("Downloaded photo %s", name)
        except Exception as exc:  # offline, blocked, etc. - the page falls back to plain colours
            log.warning("Could not download photo %s (%s)", name, exc)
