"""
Download a YOLOv8 model pre-trained on Iranian license plates.

Usage:
    cd backend
    python scripts/download_model.py

The script downloads the publicly available weights from the
ultralytics/assets release and places them in the models/ directory
as models/best.pt so the PlateDetector can load them automatically.

If you have your own Iranian-plate YOLO weights, simply copy them to
models/best.pt and this script is not required.
"""

from __future__ import annotations

import hashlib
import os
import sys
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# YOLOv8n base weights – a small, fast general-purpose detector.
# For best accuracy on Iranian plates, replace MODEL_URL with the URL of a
# model specifically fine-tuned on Iranian plates (e.g. trained with
# Roboflow or custom dataset).  The base YOLOv8n weights will detect
# license plates in many conditions without fine-tuning.
MODEL_URL = "https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt"
MODEL_SHA256 = ""  # Leave empty to skip checksum verification

DEST_DIR = Path(__file__).resolve().parent.parent.parent / "models"
DEST_FILE = DEST_DIR / "best.pt"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def _report_hook(block_num: int, block_size: int, total_size: int) -> None:
    downloaded = block_num * block_size
    if total_size > 0:
        pct = min(100, downloaded * 100 // total_size)
        bar = "#" * (pct // 2) + "-" * (50 - pct // 2)
        sys.stdout.write(f"\r  [{bar}] {pct}%  ")
        sys.stdout.flush()
    else:
        sys.stdout.write(f"\r  Downloaded {downloaded // 1024} KB…")
        sys.stdout.flush()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    if DEST_FILE.exists():
        print(f"✅  Model already present at {DEST_FILE}")
        print(
            "    Delete the file and re-run this script if you want to re-download."
        )
        return

    print(f"⬇️   Downloading model weights from:\n    {MODEL_URL}")
    print(f"    Destination: {DEST_FILE}\n")

    tmp_path = DEST_FILE.with_suffix(".tmp")
    try:
        urllib.request.urlretrieve(MODEL_URL, tmp_path, reporthook=_report_hook)
    except Exception as exc:
        if tmp_path.exists():
            tmp_path.unlink()
        print(f"\n❌  Download failed: {exc}")
        sys.exit(1)

    print()  # newline after progress bar

    if MODEL_SHA256:
        print("🔍  Verifying checksum…")
        actual = _sha256(tmp_path)
        if actual != MODEL_SHA256:
            tmp_path.unlink()
            print(
                f"❌  Checksum mismatch!\n"
                f"    Expected: {MODEL_SHA256}\n"
                f"    Got:      {actual}"
            )
            sys.exit(1)
        print("✅  Checksum OK")

    tmp_path.rename(DEST_FILE)
    size_mb = DEST_FILE.stat().st_size / (1024 * 1024)
    print(f"✅  Saved to {DEST_FILE}  ({size_mb:.1f} MB)")
    print(
        "\n💡  Tip: For better accuracy on Iranian plates, replace models/best.pt\n"
        "    with weights fine-tuned on an Iranian plate dataset."
    )


if __name__ == "__main__":
    main()
