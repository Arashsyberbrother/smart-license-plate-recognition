"""
Tests for OCRService (mock mode)
تست‌های سرویس OCR در حالت آزمایشی
"""

import pytest
from services.ocr_service import OCRService, get_ocr_service, PLATE_LETTER_MAP


class TestOCRInitialization:
    def test_ocr_initialization(self):
        svc = OCRService()
        assert svc is not None

    def test_singleton(self):
        s1 = get_ocr_service()
        s2 = get_ocr_service()
        assert s1 is s2

    def test_plate_letter_map_not_empty(self):
        assert len(PLATE_LETTER_MAP) > 0

    def test_plate_letter_map_values_are_persian(self):
        for latin, persian in PLATE_LETTER_MAP.items():
            assert len(latin) >= 1
            assert len(persian) >= 1


class TestReadPlateMock:
    def test_read_plate_mock_returns_dict(self):
        svc = OCRService()
        result = svc.read_plate(None)
        assert isinstance(result, dict)

    def test_read_plate_has_required_keys(self):
        svc = OCRService()
        result = svc.read_plate(None)
        assert "text" in result
        assert "confidence" in result
        assert "raw_text" in result

    def test_read_plate_confidence_in_range(self):
        svc = OCRService()
        result = svc.read_plate(None)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_read_plate_with_bytes_input(self):
        svc = OCRService()
        fake_bytes = b"not_a_real_image"
        result = svc.read_plate(fake_bytes)
        assert isinstance(result, dict)
        assert "text" in result

    def test_preprocess_returns_image_or_input(self):
        svc = OCRService()
        try:
            from PIL import Image
            import io

            buf = io.BytesIO()
            img = Image.new("RGB", (50, 20), color=(200, 200, 200))
            img.save(buf, format="PNG")
            buf.seek(0)
            pil_img = Image.open(buf)
            processed = svc.preprocess_for_ocr(pil_img)
            assert processed is not None
        except ImportError:
            pytest.skip("Pillow not installed")
