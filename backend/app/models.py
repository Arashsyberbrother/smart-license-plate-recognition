"""
SQLAlchemy ORM models
مدل‌های پایگاه داده
"""

from datetime import datetime, date
from sqlalchemy import (
    Boolean, Column, Date, DateTime, Float, Integer, String, func
)
from app.database import Base


class PlateRecord(Base):
    """Detected license plate record - رکورد پلاک تشخیص داده شده"""

    __tablename__ = "plate_records"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, nullable=False, index=True)
    plate_type = Column(String, nullable=False)
    province = Column(String, nullable=True)
    confidence = Column(Float, nullable=False)
    image_path = Column(String, nullable=True)
    raw_text = Column(String, nullable=True)
    is_valid = Column(Boolean, default=True, nullable=False)
    vehicle_type = Column(String, nullable=True)
    processing_time = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class SystemStats(Base):
    """Daily aggregated system statistics - آمار روزانه سیستم"""

    __tablename__ = "system_stats"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False)
    total_detections = Column(Integer, default=0, nullable=False)
    successful_detections = Column(Integer, default=0, nullable=False)
    failed_detections = Column(Integer, default=0, nullable=False)
    avg_confidence = Column(Float, default=0.0, nullable=False)
    avg_processing_time = Column(Float, default=0.0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class AccessLog(Base):
    """API access log - گزارش دسترسی به API"""

    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time = Column(Float, nullable=False)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
