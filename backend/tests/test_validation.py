"""
Tests for IranianPlateValidator
تست‌های اعتبارسنجی پلاک ایرانی
"""

import pytest
from services.validation import IranianPlateValidator, PROVINCES


@pytest.fixture()
def validator():
    return IranianPlateValidator()


class TestValidCarPlate:
    def test_valid_car_plate(self, validator):
        result = validator.validate("12ط345-11")
        assert result["is_valid"] is True
        assert result["plate_type"] == "car"

    def test_car_plate_with_province(self, validator):
        result = validator.validate("12ط345-11")
        assert result["province"] == "تهران"

    def test_car_plate_formatted(self, validator):
        result = validator.validate("12ط345-11")
        assert "12" in result["formatted"]
        assert "345" in result["formatted"]


class TestInvalidPlate:
    def test_empty_string(self, validator):
        result = validator.validate("")
        assert result["is_valid"] is False

    def test_none_like_empty(self, validator):
        result = validator.validate("   ")
        assert result["is_valid"] is False

    def test_random_text(self, validator):
        result = validator.validate("HELLO")
        assert result["is_valid"] is False

    def test_invalid_format(self, validator):
        result = validator.validate("ABC-123")
        assert result["is_valid"] is False


class TestProvinceDetection:
    def test_known_province_code(self, validator):
        province = validator.get_province("11")
        assert province == "تهران"

    def test_unknown_province_code(self, validator):
        # Code 99 maps to government/military in PROVINCES dict
        province = validator.get_province("99")
        assert province == "دولتی / نظامی"

    def test_all_provinces_non_empty(self):
        for code, name in PROVINCES.items():
            assert name, f"Province name for code {code} is empty"


class TestMotorcyclePlate:
    def test_motorcycle_format(self, validator):
        result = validator.validate("123تس-11")
        assert result["plate_type"] == "motorcycle"

    def test_motorcycle_is_valid(self, validator):
        result = validator.validate("456لم-21")
        assert result["is_valid"] is True


class TestPlateFormatting:
    def test_car_plate_formatting(self, validator):
        result = validator.validate("12ط345-11")
        fmt = result["formatted"]
        assert "-" in fmt or len(fmt) > 5

    def test_detect_plate_type_car(self, validator):
        assert validator.detect_plate_type("12ط345-11") == "car"

    def test_detect_plate_type_motorcycle(self, validator):
        assert validator.detect_plate_type("123تس-11") == "motorcycle"

    def test_detect_plate_type_unknown(self, validator):
        assert validator.detect_plate_type("UNKNOWN") == "unknown"
