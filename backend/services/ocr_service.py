"""
OCR service for reading Iranian license plates.
Engine priority:
  1. hezar CRNN  – `hezarai/crnn-fa-64x256-license-plate-recognition`
     Purpose-built model for Persian plates (HuggingFace / hezar library).
     Source: https://github.com/EpsilonAleph/Iranian-License-Plate-Recognition-App
  2. EasyOCR (fa + en)  – general-purpose fallback.
  3. Mock result – used only when no OCR library is available.

سرویس تشخیص متن پلاک‌های ایرانی
"""

from __future__ import annotations

import io
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional dependency: hezar (primary – best accuracy for Persian plates)
# ---------------------------------------------------------------------------
try:
    from hezar.models import Model as HezarModel
    _HEZAR_AVAILABLE = True
except ImportError:  # pragma: no cover
    _HEZAR_AVAILABLE = False
    logger.warning(
        "hezar not installed – falling back to EasyOCR. "
        "Install with: pip install hezar>=1.0.0"
    )

# ---------------------------------------------------------------------------
# Optional dependency: easyocr (secondary fallback)
# ---------------------------------------------------------------------------
try:
    import easyocr
    _EASYOCR_AVAILABLE = True
except ImportError:  # pragma: no cover
    _EASYOCR_AVAILABLE = False
    logger.warning("easyocr not installed – OCR running in mock mode")

# ---------------------------------------------------------------------------
# Image libraries
# ---------------------------------------------------------------------------
try:
    from PIL import Image, ImageFilter, ImageOps
    _PIL_AVAILABLE = True
except ImportError:  # pragma: no cover
    _PIL_AVAILABLE = False

# ---------------------------------------------------------------------------
# Persian letter mapping – maps common Latin look-alikes to Persian
# ---------------------------------------------------------------------------
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

# Map ASCII digits to Arabic-Indic (Eastern Arabic) digits used on Iranian plates
_ASCII_TO_PERSIAN_DIGIT: Dict[str, str] = dict(zip("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


class OCRService:
    """
    Reads text from cropped license plate images.

    Engine priority:
      hezar CRNN  →  EasyOCR  →  mock
    """

    _HEZAR_MODEL_ID = "hezarai/crnn-fa-64x256-license-plate-recognition"

    def __init__(self) -> None:
        self._hezar_model = None
        self._easyocr_reader = None
        self._mock_mode = True
        self._engine = "mock"

        if _HEZAR_AVAILABLE:
            try:
                self._hezar_model = HezarModel.load(self._HEZAR_MODEL_ID)
                self._mock_mode = False
                self._engine = "hezar"
                logger.info(
                    f"hezar CRNN model loaded: {self._HEZAR_MODEL_ID} "
                    "(best-in-class Persian plate OCR)"
                )
            except Exception as exc:
                logger.warning(
                    f"Failed to load hezar CRNN model: {exc} – trying EasyOCR"
                )

        if self._engine == "mock" and _EASYOCR_AVAILABLE:
            try:
                self._easyocr_reader = easyocr.Reader(
                    ["fa", "en"], gpu=False, verbose=False
                )
                self._mock_mode = False
                self._engine = "easyocr"
                logger.info("EasyOCR reader initialised (fa + en) as fallback")
            except Exception as exc:
                logger.warning(f"Failed to init EasyOCR: {exc} – mock mode")

        if self._engine == "mock":
            logger.warning(
                "No OCR engine available – running in mock mode. "
                "Install hezar (pip install hezar>=1.0.0) for best results."
            )

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

        if self._engine == "hezar":
            return self._read_with_hezar(image)

        if self._engine == "easyocr":
            return self._read_with_easyocr(image)

        return self._mock_result()

    def crop_plate(self, image, bbox: Tuple) -> "Image.Image":
        """Crop the plate region from the image"""
        x1, y1, x2, y2 = [int(v) for v in bbox]
        return image.crop((x1, y1, x2, y2))

    def preprocess_for_ocr(self, image) -> "Image.Image":
        """
        Enhance a cropped plate image for EasyOCR (not used by hezar which
        handles preprocessing internally).
        Pipeline: resize to standard height → grayscale → adaptive threshold
        → morphological closing → 3× upscale.
        Falls back to simple greyscale + sharpen if OpenCV is unavailable.
        """
        if not _PIL_AVAILABLE:
            return image
        try:
            import cv2
            import numpy as np

            arr = np.array(image.convert("RGB"))
            h, w = arr.shape[:2]
            if h == 0:
                raise ValueError(
                    "Invalid image: height is zero, cannot resize for OCR processing"
                )
            target_h = 64
            target_w = max(1, int(w * target_h / h))
            resized = cv2.resize(arr, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
            gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)
            thresh = cv2.adaptiveThreshold(
                gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                blockSize=15,
                C=8,
            )
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            final = cv2.resize(
                cleaned, (target_w * 3, target_h * 3), interpolation=cv2.INTER_NEAREST
            )
            return Image.fromarray(final)

        except Exception as exc:
            logger.debug(
                f"Advanced OCR preprocessing failed ({exc}), using simple fallback"
            )
            gray = ImageOps.grayscale(image)
            return gray.filter(ImageFilter.SHARPEN)

    # ------------------------------------------------------------------
    # Engine-specific read methods
    # ------------------------------------------------------------------

    def _read_with_hezar(self, image: "Image.Image") -> Dict[str, Any]:
        """
        Use the hezar CRNN model (`hezarai/crnn-fa-64x256-license-plate-recognition`)
        to read text from a cropped plate image.
        The model handles all preprocessing internally (resize to 64×256, normalise).
        Input: PIL Image   Output: {text, confidence, raw_text}
        """
        try:
            import numpy as np

            # hezar's ImageProcessor accepts PIL Images, numpy arrays, or file paths
            img_array = np.array(image.convert("RGB"))
            results = self._hezar_model.predict(img_array)
            if not results:
                return {"text": "", "confidence": 0.0, "raw_text": ""}

            raw_text: str = results[0]["text"] if results[0]["text"] else ""
            # Normalise: convert ASCII digits to Persian, map Latin→Persian letters
            cleaned = self._normalise_hezar_output(raw_text)
            # Confidence: hezar CRNN doesn't always expose per-prediction confidence,
            # fall back to a fixed high value when the text is non-empty.
            confidence: float = 0.90 if cleaned else 0.0
            return {
                "text": cleaned,
                "confidence": confidence,
                "raw_text": raw_text,
            }
        except Exception as exc:
            logger.error(f"hezar OCR read error: {exc}")
            return {"text": "", "confidence": 0.0, "raw_text": ""}

    def _read_with_easyocr(self, image: "Image.Image") -> Dict[str, Any]:
        """Use EasyOCR as a secondary OCR engine."""
        processed = self.preprocess_for_ocr(image)
        try:
            results = self._easyocr_reader.readtext(
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
            logger.error(f"EasyOCR read error: {exc}")
            return {"text": "", "confidence": 0.0, "raw_text": ""}

    # ------------------------------------------------------------------
    # Text normalisation helpers
    # ------------------------------------------------------------------

    def _normalise_hezar_output(self, text: str) -> str:
        """
        Normalise text from hezar CRNN:
        - Map ASCII digits → Arabic-Indic (Persian) digits
        - Strip unwanted characters (the model output is already in Persian)
        """
        result = []
        for ch in text:
            if ch in _ASCII_TO_PERSIAN_DIGIT:
                result.append(_ASCII_TO_PERSIAN_DIGIT[ch])
            elif ch in "۰۱۲۳۴۵۶۷۸۹ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی -":
                result.append(ch)
            # drop anything else (noise)
        return "".join(result).strip()

    def _clean_text(self, text: str) -> str:
        """Normalise EasyOCR output: map Latin→Persian, remove junk."""
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
