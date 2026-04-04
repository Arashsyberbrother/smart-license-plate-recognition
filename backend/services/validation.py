"""
Iranian license plate validation
اعتبارسنجی پلاک‌های ایرانی
"""

from __future__ import annotations

import re
from typing import Dict, Optional

# ---------------------------------------------------------------------------
# Province code -> province name mapping (2-digit codes on Iranian plates)
# ---------------------------------------------------------------------------

PROVINCES: Dict[str, str] = {
    "11": "تهران",
    "12": "تهران",
    "13": "تهران",
    "14": "تهران",
    "15": "البرز",
    "21": "اصفهان",
    "22": "اصفهان",
    "23": "یزد",
    "24": "کرمان",
    "25": "فارس",
    "26": "فارس",
    "27": "خوزستان",
    "28": "خوزستان",
    "31": "خراسان رضوی",
    "32": "خراسان رضوی",
    "33": "خراسان رضوی",
    "34": "خراسان جنوبی",
    "35": "خراسان شمالی",
    "41": "آذربایجان شرقی",
    "42": "آذربایجان غربی",
    "43": "اردبیل",
    "44": "زنجان",
    "45": "گیلان",
    "46": "مازندران",
    "47": "مازندران",
    "48": "گلستان",
    "51": "کرمانشاه",
    "52": "همدان",
    "53": "لرستان",
    "54": "ایلام",
    "55": "کردستان",
    "56": "سمنان",
    "57": "قم",
    "58": "مرکزی",
    "61": "بوشهر",
    "62": "هرمزگان",
    "63": "سیستان و بلوچستان",
    "64": "چهارمحال و بختیاری",
    "65": "کهگیلویه و بویراحمد",
    "66": "گلستان",
    "67": "قزوین",
    "68": "گیلان",
    "71": "خراسان رضوی",
    "77": "تهران",
    "78": "تهران",
    "79": "تهران",
    "99": "دولتی / نظامی",
}

# Valid Persian letters used on Iranian plates
VALID_LETTERS: set = set("ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی")

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Standard car plate: 2 digits + 1 Persian letter + 3 digits + 2 digits
# Example: ۱۲ط۳۴۵-۱۱  or  12T345-11
_CAR_PATTERN = re.compile(
    r"^(\d{1,2})([\u0600-\u06FFa-zA-Z]{1})(\d{3})[- ]?(\d{2})$"
)

# Motorcycle plate: 3 digits + 2 Persian letters + 2 digits
_MOTO_PATTERN = re.compile(
    r"^(\d{3})([\u0600-\u06FFa-zA-Z]{2})[- ]?(\d{2})$"
)

# Government / Taxi might have different formats; a loose pattern
_GOV_PATTERN = re.compile(r"^[۰-۹0-9]{2,3}[^\d]{0,2}[۰-۹0-9]{2,5}$")


class IranianPlateValidator:
    """Validates and parses Iranian license plates"""

    def validate(self, plate_text: str) -> Dict:
        """
        Validate a raw plate string.
        Returns: {is_valid, plate_type, province, formatted, message}
        """
        if not plate_text or not plate_text.strip():
            return self._invalid("Empty plate text")

        text = plate_text.strip()
        plate_type = self.detect_plate_type(text)

        if plate_type == "car":
            m = _CAR_PATTERN.match(text)
            if m:
                prefix, letter, middle, province_code = m.groups()
                province = self.get_province(province_code)
                formatted = self.format_plate(text, plate_type)
                return {
                    "is_valid": True,
                    "plate_type": plate_type,
                    "province": province,
                    "formatted": formatted,
                    "message": "Valid car plate",
                }

        elif plate_type == "motorcycle":
            m = _MOTO_PATTERN.match(text)
            if m:
                digits1, letters, province_code = m.groups()
                province = self.get_province(province_code)
                formatted = self.format_plate(text, plate_type)
                return {
                    "is_valid": True,
                    "plate_type": plate_type,
                    "province": province,
                    "formatted": formatted,
                    "message": "Valid motorcycle plate",
                }

        elif plate_type in ("taxi", "government"):
            return {
                "is_valid": True,
                "plate_type": plate_type,
                "province": None,
                "formatted": text,
                "message": f"Valid {plate_type} plate",
            }

        return self._invalid(f"Unrecognized plate format: {plate_text}")

    # ------------------------------------------------------------------

    def detect_plate_type(self, text: str) -> str:
        """Determine the plate type from its text"""
        if _CAR_PATTERN.match(text):
            return "car"
        if _MOTO_PATTERN.match(text):
            return "motorcycle"
        # Taxi plates often contain 'T' or 'taxi' prefix
        if re.search(r"[Tت][Aاa][Xخx][Iیi]", text, re.IGNORECASE):
            return "taxi"
        # Government plates start with specific codes
        if re.match(r"^(99|۹۹|[A-Za-z]{1,3}\d)", text):
            return "government"
        return "unknown"

    def format_plate(self, text: str, plate_type: str) -> str:
        """Return a human-readable formatted plate string"""
        if plate_type == "car":
            m = _CAR_PATTERN.match(text)
            if m:
                prefix, letter, middle, province_code = m.groups()
                return f"{prefix}{letter}{middle}-{province_code}"
        if plate_type == "motorcycle":
            m = _MOTO_PATTERN.match(text)
            if m:
                digits1, letters, province_code = m.groups()
                return f"{digits1}{letters}-{province_code}"
        return text

    def get_province(self, code: str) -> Optional[str]:
        """Return province name for a given 2-digit province code"""
        return PROVINCES.get(str(code).zfill(2))

    # ------------------------------------------------------------------

    @staticmethod
    def _invalid(message: str) -> Dict:
        return {
            "is_valid": False,
            "plate_type": "unknown",
            "province": None,
            "formatted": "",
            "message": message,
        }
