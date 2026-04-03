"""
YOLOv8 license plate detector service
سرویس تشخیص پلاک با YOLOv8
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
    logger.warning("ultralytics not installed – running in mock mode")

try:
    from PIL import Image, ImageDraw, ImageFont
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False


class PlateDetector:
    """
    Detects license plates in images using YOLOv8.
    Falls back to mock mode when the model file or library is unavailable.
    """

    def __init__(self, model_path: str, confidence_threshold: float = 0.85) -> None:
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self._model = None
        self._mock_mode = True

        if _YOLO_AVAILABLE:
            import os
            candidate = os.path.join(model_path, "best.pt")
            if os.path.isfile(candidate):
                try:
                    self._model = YOLO(candidate)
                    self._mock_mode = False
                    logger.info(f"YOLOv8 model loaded from {candidate}")
                except Exception as exc:
                    logger.warning(f"Failed to load YOLO model: {exc} – mock mode")
            else:
                logger.warning(f"Model file not found at {candidate} – mock mode")
        else:
            logger.info("PlateDetector initialised in mock mode (no ultralytics)")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Run plate detection on raw image bytes.
        Returns a list of detection dicts: {bbox, confidence, area}
        """
        if self._mock_mode:
            return self._mock_detection()

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

    @staticmethod
    def _mock_detection() -> List[Dict[str, Any]]:
        """Return a single synthetic detection used when no model is available"""
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
