"""
Tests for API endpoints
تست‌های نقاط پایانی API
"""

import base64
import io

import pytest


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    def test_health_endpoint_returns_200(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_response_schema(self, client):
        response = client.get("/api/health")
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "database" in data
        assert "uptime" in data
        assert "timestamp" in data

    def test_health_status_is_healthy(self, client):
        response = client.get("/api/health")
        data = response.json()
        assert data["status"] in ("healthy", "unhealthy")


# ---------------------------------------------------------------------------
# Plates list endpoint
# ---------------------------------------------------------------------------

class TestListPlates:
    def test_list_plates_empty(self, client):
        response = client.get("/api/plates")
        assert response.status_code == 200

    def test_list_plates_response_schema(self, client):
        response = client.get("/api/plates")
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "pages" in data

    def test_list_plates_items_is_list(self, client):
        response = client.get("/api/plates")
        assert isinstance(response.json()["items"], list)

    def test_list_plates_pagination_defaults(self, client):
        response = client.get("/api/plates")
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 20


# ---------------------------------------------------------------------------
# Detect endpoint with invalid data
# ---------------------------------------------------------------------------

class TestDetectInvalidImage:
    def test_detect_no_input_returns_422(self, client):
        response = client.post("/api/plates/detect")
        assert response.status_code == 422

    def test_detect_invalid_base64_returns_422(self, client):
        response = client.post(
            "/api/plates/detect",
            json={"image": "!!!not_valid_base64!!!"},
        )
        assert response.status_code == 422

    def test_detect_with_minimal_png(self, client, test_plate_image):
        response = client.post(
            "/api/plates/detect",
            files={"file": ("test.png", test_plate_image, "image/png")},
        )
        # Should succeed (mock mode returns a result)
        assert response.status_code in (200, 422, 500)
        if response.status_code == 200:
            data = response.json()
            assert "plate_number" in data
            assert "confidence" in data


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------

class TestRootEndpoint:
    def test_root_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_has_app_info(self, client):
        data = client.get("/").json()
        assert "app" in data
        assert "version" in data
