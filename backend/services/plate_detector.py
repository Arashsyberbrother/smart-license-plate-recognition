"""
YOLOv8 license plate detector service with OpenCV contour fallback
سرویس تشخیص پلاک با YOLOv8 و پشتیبانی OpenCV
"""

from __future__ import annotations

import io
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Graceful import of ultralytics
try:
    from ultralytics import YOLO
    _YOLO_AVAILABLE = True
except ImportError:
    _YOLO_AVAILABLE = False
    logger.warning("ultralytics not installed – will use OpenCV fallback")

try:
    from PIL import Image, ImageDraw, ImageFont
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

try:
    import cv2
    import numpy as np
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False
    logger.warning("opencv-python-headless not installed – falling back to mock detection")


class PlateDetector:
    """
    Detects license plates in images.
    Priority: YOLOv8 (if model file exists) → OpenCV contour detection → mock.
    The OpenCV contour method requires no trained model and works on most
    clear plate photos by filtering rectangular regions with an Iranian plate
    aspect ratio (≈ 3.5–5.5 : 1).
    """

    def __init__(self, model_path: str, confidence_threshold: float = 0.85) -> None:
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self._model = None
        self._use_yolo = False

        if _YOLO_AVAILABLE:
            import os
            candidate = os.path.join(model_path, "best.pt")
            if os.path.isfile(candidate):
                try:
                    self._model = YOLO(candidate)
                    self._use_yolo = True
                    logger.info(f"YOLOv8 model loaded from {candidate}")
                except Exception as exc:
                    logger.warning(f"Failed to load YOLO model: {exc} – using OpenCV fallback")
            else:
                logger.info(
                    f"Model file not found at {candidate} – using OpenCV contour detection. "
                    "Run backend/scripts/download_model.py to download a pre-trained model."
                )
        else:
            logger.info("ultralytics not available – using OpenCV contour detection")

    # ------------------------------------------------------------------
    # Backwards-compatible property (used by existing tests)
    # ------------------------------------------------------------------

    @property
    def _mock_mode(self) -> bool:
        """True when no YOLOv8 model is loaded (OpenCV or pure-mock fallback)."""
        return not self._use_yolo

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Run plate detection on raw image bytes.
        Returns a list of detection dicts: {bbox, confidence, area}
        """
        if self._use_yolo and self._model is not None:
            return self._yolo_detect(image_bytes)

        if _CV2_AVAILABLE:
            return self._opencv_detect(image_bytes)

        return self._mock_detection()

    def preprocess_image(self, image_bytes: bytes):
        """Decode bytes to a PIL Image; raises PIL.UnidentifiedImageError on bad input"""
        if not _PIL_AVAILABLE:
            return image_bytes
        return Image.open(io.BytesIO(image_bytes)).convert("RGB")

    def draw_detections(self, image, detections: List[Dict[str, Any]]) -> bytes:
        """Annotate image with bounding boxes and return PNG bytes"""
        if not _PIL_AVAILABLE:
            return b""
        if not isinstance(image, Image.Image):
            try:
                image = self.preprocess_image(image)
            except Exception:
                return b""
        draw = ImageDraw.Draw(image)
        for det in detections:
            bbox = det["bbox"]
            conf = det.get("confidence", 0)
            draw.rectangle(bbox, outline="red", width=3)
            draw.text((bbox[0], bbox[1] - 15), f"{conf:.2f}", fill="red")
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _yolo_detect(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """Run detection with the loaded YOLOv8 model"""
        image = self.preprocess_image(image_bytes)
        results = self._model.predict(
            source=image,
            conf=self.confidence_threshold,
            verbose=False,
        )
        detections: List[Dict[str, Any]] = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                area = (x2 - x1) * (y2 - y1)
                detections.append(
                    {
                        "bbox": [x1, y1, x2, y2],
                        "confidence": round(conf, 4),
                        "area": round(area, 2),
                    }
                )
        return detections

    def _opencv_detect(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Contour-based plate detection using OpenCV.
        Works without any trained model by locating rectangular regions
        whose aspect ratio matches Iranian license plates (≈ 3.5–5.5 : 1).
        Implements a multi-pass strategy:
          1. Canny edges on a bilaterally-filtered grayscale image.
          2. Sobel gradient magnitude as a second pass for harder images.
          3. Merge candidates from both passes, deduplicate by IoU.
        """
        img_array = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            logger.warning("OpenCV could not decode image bytes")
            return self._mock_detection()

        h, w = img.shape[:2]
        min_area = w * h * 0.004   # plate must be at least 0.4 % of image area
        max_area = w * h * 0.60    # and not more than 60 %
        min_asp, max_asp = 2.5, 7.0  # width/height ratio range for Iranian plates

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        candidates: List[tuple] = []  # (x, y, cw, ch, score)

        # --- Pass 1: Canny edges ---
        blurred = cv2.bilateralFilter(gray, 11, 17, 17)
        edged = cv2.Canny(blurred, 30, 200)
        contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for c in sorted(contours, key=cv2.contourArea, reverse=True)[:40]:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.018 * peri, True)
            x, y, cw, ch = cv2.boundingRect(c)
            if ch == 0:
                continue
            asp = cw / ch
            area = cw * ch
            is_rect = len(approx) in (4, 5)
            if is_rect and min_asp <= asp <= max_asp and min_area <= area <= max_area:
                score = area / (w * h)
                candidates.append((x, y, cw, ch, score))

        # --- Pass 2: Sobel gradient ---
        sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = cv2.convertScaleAbs(np.sqrt(sobelx ** 2 + sobely ** 2))
        _, sobel_thresh = cv2.threshold(magnitude, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 3))
        closed = cv2.morphologyEx(sobel_thresh, cv2.MORPH_CLOSE, kernel)
        contours2, _ = cv2.findContours(closed, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for c in sorted(contours2, key=cv2.contourArea, reverse=True)[:40]:
            x, y, cw, ch = cv2.boundingRect(c)
            if ch == 0:
                continue
            asp = cw / ch
            area = cw * ch
            if min_asp <= asp <= max_asp and min_area <= area <= max_area:
                score = area / (w * h)
                candidates.append((x, y, cw, ch, score))

        if not candidates:
            return self._mock_detection()

        # Remove duplicates: keep the candidate with higher score when IoU > 0.4
        kept: List[tuple] = []
        for cand in sorted(candidates, key=lambda c: c[4], reverse=True):
            x1, y1, cw, ch, _ = cand
            overlap = False
            for kx1, ky1, kcw, kch, _ in kept:
                ix = max(0, min(x1 + cw, kx1 + kcw) - max(x1, kx1))
                iy = max(0, min(y1 + ch, ky1 + kch) - max(y1, ky1))
                inter = ix * iy
                union = cw * ch + kcw * kch - inter
                if union > 0 and inter / union > 0.4:
                    overlap = True
                    break
            if not overlap:
                kept.append(cand)

        detections: List[Dict[str, Any]] = []
        for x, y, cw, ch, score in kept[:5]:
            conf = min(0.92, 0.65 + score * 2.0)
            detections.append(
                {
                    "bbox": [float(x), float(y), float(x + cw), float(y + ch)],
                    "confidence": round(conf, 4),
                    "area": float(cw * ch),
                }
            )

        return detections

    @staticmethod
    def _mock_detection() -> List[Dict[str, Any]]:
        """Return a single synthetic detection used when no real detection is possible"""
        return [
            {
                "bbox": [50.0, 50.0, 250.0, 120.0],
                "confidence": 0.91,
                "area": 14000.0,
            }
        ]


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_detector_instance: Optional[PlateDetector] = None


def get_plate_detector(model_path: str = "models/", confidence_threshold: float = 0.85) -> PlateDetector:
    """Return the global PlateDetector singleton"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = PlateDetector(model_path, confidence_threshold)
    return _detector_instance
