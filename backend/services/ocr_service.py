"""
EasyOCR service for reading Iranian license plates
سرویس تشخیص متن پلاک‌های ایرانی
"""

from __future__ import annotations

import io
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

try:
    import easyocr
    _EASYOCR_AVAILABLE = True
except ImportError:
    _EASYOCR_AVAILABLE = False
    logger.warning("easyocr not installed – OCR running in mock mode")

try:
    from PIL import Image, ImageFilter, ImageOps
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

# ---------------------------------------------------------------------------
# Persian letter mapping used in Iranian plates
# ---------------------------------------------------------------------------

# Maps common OCR mis-reads and Latin look-alikes to their Persian equivalents
PLATE_LETTER_MAP: Dict[str, str] = {
    "A": "ا",
    "B": "ب",
    "P": "پ",
    "T": "ت",
    "S": "س",
    "J": "ج",
    "H": "ح",
    "D": "د",
    "R": "ر",
    "Z": "ز",
    "F": "ف",
    "Q": "ق",
    "K": "ک",
    "G": "گ",
    "L": "ل",
    "M": "م",
    "N": "ن",
    "V": "و",
    "W": "و",
    "Y": "ی",
    "I": "ی",
    "E": "ع",
    "O": "۰",
    "X": "خ",
    "C": "ک",
    "U": "و",
}


class OCRService:
    """
    Reads text from cropped license plate images.
    Falls back to mock mode when easyocr is unavailable.
    """

    def __init__(self) -> None:
        self._reader = None
        self._mock_mode = True

        if _EASYOCR_AVAILABLE:
            try:
                self._reader = easyocr.Reader(["fa", "en"], gpu=False, verbose=False)
                self._mock_mode = False
                logger.info("EasyOCR reader initialised (fa + en)")
            except Exception as exc:
                logger.warning(f"Failed to init EasyOCR: {exc} – mock mode")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def read_plate(self, image, bbox: Optional[Tuple] = None) -> Dict[str, Any]:
        """
        Read plate text from a PIL Image (or raw bytes).
        bbox is (x1, y1, x2, y2); if supplied the image is cropped first.
        Returns: {text, confidence, raw_text}
        """
        if not _PIL_AVAILABLE or image is None:
            return self._mock_result()

        if isinstance(image, bytes):
            try:
                image = Image.open(io.BytesIO(image)).convert("RGB")
            except Exception:
                return self._mock_result()

        if bbox:
            image = self.crop_plate(image, bbox)

        processed = self.preprocess_for_ocr(image)

        if self._mock_mode:
            return self._mock_result()

        try:
            results = self._reader.readtext(
                processed,
                allowlist="0123456789ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی",
                detail=1,
            )
            if not results:
                return {"text": "", "confidence": 0.0, "raw_text": ""}

            raw_parts: List[str] = []
            confidences: List[float] = []
            for _, text, conf in results:
                raw_parts.append(text)
                confidences.append(conf)

            raw_text = " ".join(raw_parts)
            avg_conf = sum(confidences) / len(confidences)
            cleaned = self._clean_text(raw_text)
            return {
                "text": cleaned,
                "confidence": round(avg_conf, 4),
                "raw_text": raw_text,
            }
        except Exception as exc:
            logger.error(f"OCR read error: {exc}")
            return {"text": "", "confidence": 0.0, "raw_text": ""}

    def crop_plate(self, image, bbox: Tuple) -> "Image.Image":
        """Crop the plate region from the image"""
        x1, y1, x2, y2 = [int(v) for v in bbox]
        return image.crop((x1, y1, x2, y2))

    def preprocess_for_ocr(self, image) -> "Image.Image":
        """
        Enhance a cropped plate image for better EasyOCR accuracy.
        Pipeline: resize to standard height → grayscale → adaptive threshold
        → morphological closing → sharpen.
        Falls back to simple greyscale + sharpen if OpenCV is unavailable.
        """
        if not _PIL_AVAILABLE:
            return image
        try:
            import cv2
            import numpy as np

            arr = np.array(image.convert("RGB"))
            # Resize to fixed height (64 px) preserving aspect ratio
            h, w = arr.shape[:2]
            if h == 0:
                raise ValueError("Invalid image: height is zero, cannot resize for OCR processing")
            target_h = 64
            target_w = max(1, int(w * target_h / h))
            resized = cv2.resize(arr, (target_w, target_h), interpolation=cv2.INTER_CUBIC)

            # Convert to grayscale
            gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)

            # Adaptive thresholding works better than global Otsu on uneven lighting
            thresh = cv2.adaptiveThreshold(
                gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                blockSize=15,
                C=8,
            )

            # Small closing to connect broken character strokes
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

            # Scale back up so EasyOCR has enough pixels to work with
            final = cv2.resize(cleaned, (target_w * 3, target_h * 3), interpolation=cv2.INTER_NEAREST)
            return Image.fromarray(final)

        except Exception as exc:
            logger.debug(f"Advanced OCR preprocessing failed ({exc}), using simple fallback")
            gray = ImageOps.grayscale(image)
            return gray.filter(ImageFilter.SHARPEN)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _clean_text(self, text: str) -> str:
        """Normalise OCR output: map Latin to Persian, remove junk"""
        result = []
        for ch in text.upper():
            if ch in PLATE_LETTER_MAP:
                result.append(PLATE_LETTER_MAP[ch])
            elif ch.isdigit() or ch in "۰۱۲۳۴۵۶۷۸۹ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی ":
                result.append(ch)
        return "".join(result).strip()

    @staticmethod
    def _mock_result() -> Dict[str, Any]:
        return {
            "text": "۱۲ط۳۴۵-۱۱",
            "confidence": 0.88,
            "raw_text": "12T345-11",
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_ocr_instance: Optional[OCRService] = None


def get_ocr_service() -> OCRService:
    """Return the global OCRService singleton"""
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = OCRService()
    return _ocr_instance
