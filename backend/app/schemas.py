"""
Pydantic schemas for request/response validation
اسکیماهای اعتبارسنجی درخواست و پاسخ
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class PlateDetectionRequest(BaseModel):
    """Request body for base64 image detection"""
    image: str = Field(..., description="Base64-encoded image data")


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class PlateDetectionResponse(BaseModel):
    """Detection result returned to the client"""
    plate_number: str
    plate_type: str
    province: Optional[str] = None
    confidence: float
    is_valid: bool
    vehicle_type: Optional[str] = None
    processing_time: float
    raw_text: Optional[str] = None
    image_path: Optional[str] = None
    message: str = "Detection successful"


# ---------------------------------------------------------------------------
# Database record schemas
# ---------------------------------------------------------------------------

class PlateRecordCreate(BaseModel):
    """Data required to create a new plate record"""
    plate_number: str
    plate_type: str
    province: Optional[str] = None
    confidence: float
    image_path: Optional[str] = None
    raw_text: Optional[str] = None
    is_valid: bool = True
    vehicle_type: Optional[str] = None
    processing_time: float


class PlateRecordResponse(PlateRecordCreate):
    """Plate record as returned from the database"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# List / pagination
# ---------------------------------------------------------------------------

class PlateListResponse(BaseModel):
    """Paginated list of plate records"""
    items: List[PlateRecordResponse]
    total: int
    page: int
    per_page: int
    pages: int


# ---------------------------------------------------------------------------
# Dashboard & analytics
# ---------------------------------------------------------------------------

class DashboardStats(BaseModel):
    """High-level dashboard statistics"""
    total_detections: int
    today_detections: int
    success_rate: float
    avg_confidence: float
    avg_processing_time: float
    recent_plates: List[Dict[str, Any]] = []


class AnalyticsResponse(BaseModel):
    """Generic analytics payload"""
    period: str
    data: List[Dict[str, Any]]
    summary: Dict[str, Any] = {}


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    database: str
    uptime: float
    timestamp: str
