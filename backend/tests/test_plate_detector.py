"""
Tests for PlateDetector (mock mode)
تست‌های تشخیص‌دهنده پلاک در حالت آزمایشی
"""

import pytest
from services.plate_detector import PlateDetector, get_plate_detector


class TestDetectorInitialization:
    def test_detector_initialization(self):
        detector = PlateDetector(model_path="nonexistent_path/", confidence_threshold=0.85)
        assert detector is not None
        assert detector.confidence_threshold == 0.85

    def test_detector_mock_mode_when_no_model(self):
        detector = PlateDetector(model_path="nonexistent_path/")
        assert detector._mock_mode is True

    def test_singleton_returns_same_instance(self):
        d1 = get_plate_detector()
        d2 = get_plate_detector()
        assert d1 is d2


class TestDetectReturnsList:
    def test_detect_returns_list(self):
        detector = PlateDetector(model_path="nonexistent_path/")
        result = detector.detect(b"fake_image_bytes")
        assert isinstance(result, list)

    def test_detect_non_empty_in_mock_mode(self):
        detector = PlateDetector(model_path="nonexistent_path/")
        result = detector.detect(b"fake_image_bytes")
        assert len(result) > 0

    def test_detect_result_structure(self):
        detector = PlateDetector(model_path="nonexistent_path/")
        result = detector.detect(b"fake_image_bytes")
        assert "bbox" in result[0]
        assert "confidence" in result[0]
        assert "area" in result[0]


class TestMockDetection:
    def test_mock_detection_bbox_is_list(self):
        detector = PlateDetector(model_path="nonexistent_path/")
        result = detector.detect(b"bytes")
        assert isinstance(result[0]["bbox"], list)
        assert len(result[0]["bbox"]) == 4

    def test_mock_detection_confidence_in_range(self):
        detector = PlateDetector(model_path="nonexistent_path/")
        result = detector.detect(b"bytes")
        assert 0.0 <= result[0]["confidence"] <= 1.0

    def test_draw_detections_returns_bytes_or_empty(self):
        detector = PlateDetector(model_path="nonexistent_path/")
        detections = detector.detect(b"bytes")
        output = detector.draw_detections(b"bytes", detections)
        assert isinstance(output, bytes)
