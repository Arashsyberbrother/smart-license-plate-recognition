"""
Download a YOLOv8 model trained on Iranian license plates.

Usage:
    cd backend
    python scripts/download_model.py

The script downloads the plate-detector.pt weights from the
barzansaeedpour/ANPR-YOLOv8 GitHub repository (committed directly
in-tree, MIT license) and places them in the models/ directory as
models/best.pt so the PlateDetector can load them automatically.

Source repository: https://github.com/barzansaeedpour/ANPR-YOLOv8

Note: For OCR (reading the plate characters), the backend uses the
hezar CRNN model `hezarai/crnn-fa-64x256-license-plate-recognition`
which is downloaded automatically from Hugging Face on first startup.
No manual step is required for that model.
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

# YOLOv8m model fine-tuned for Iranian license plate detection.
# Source: barzansaeedpour/ANPR-YOLOv8 (MIT)
# Direct commit URL (stable, will not change even when the branch moves):
# Pinned commit from 2023-11-12 (initial training run, MIT license)
_COMMIT = "c21d45d1c6313050b6566067a6234cb41a046d92"
MODEL_URL = (
    f"https://raw.githubusercontent.com/barzansaeedpour/ANPR-YOLOv8/"
    f"{_COMMIT}/models/plate-detector.pt"
)
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

    print("📥  Iranian license plate detection model")
    print(f"    Source: barzansaeedpour/ANPR-YOLOv8 (MIT)")
    print(f"    URL:    {MODEL_URL}")
    print(f"    Dest:   {DEST_FILE}\n")

    tmp_path = DEST_FILE.with_suffix(".tmp")
    try:
        urllib.request.urlretrieve(MODEL_URL, tmp_path, reporthook=_report_hook)
    except Exception as exc:
        if tmp_path.exists():
            tmp_path.unlink()
        print(f"\n❌  Download failed: {exc}")
        print(
            "\n💡  If the download fails, manually copy the file:\n"
            f"    1. Open https://github.com/barzansaeedpour/ANPR-YOLOv8/blob/{_COMMIT}/models/plate-detector.pt\n"
            f"    2. Click 'Download raw file'\n"
            f"    3. Save it to: {DEST_FILE}"
        )
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
        "\n💡  The OCR model (hezar CRNN) is downloaded automatically from\n"
        "    Hugging Face on the first backend startup – no manual step needed.\n"
        "\n    Start the backend with:\n"
        "       docker-compose up -d\n"
        "    or:\n"
        "       cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    )


if __name__ == "__main__":
    main()
