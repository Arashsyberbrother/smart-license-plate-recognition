"""
Analytics service for aggregated statistics
سرویس تحلیل آمار تجمعی
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AccessLog, PlateRecord, SystemStats

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Provides analytical queries over stored plate detection data"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Time-series
    # ------------------------------------------------------------------

    async def get_daily_stats(self, days: int = 30) -> List[Dict[str, Any]]:
        """Return per-day detection counts for the last `days` days"""
        since = datetime.utcnow() - timedelta(days=days)
        stmt = (
            select(
                func.date(PlateRecord.created_at).label("day"),
                func.count(PlateRecord.id).label("total"),
                func.sum(
                    func.cast(PlateRecord.is_valid, type_=None)
                ).label("valid"),
                func.avg(PlateRecord.confidence).label("avg_confidence"),
            )
            .where(PlateRecord.created_at >= since)
            .group_by(func.date(PlateRecord.created_at))
            .order_by(func.date(PlateRecord.created_at))
        )
        result = await self.db.execute(stmt)
        rows = result.fetchall()
        return [
            {
                "date": str(row.day),
                "total": row.total,
                "valid": int(row.valid or 0),
                "avg_confidence": round(float(row.avg_confidence or 0), 4),
            }
            for row in rows
        ]

    async def get_hourly_stats(self, target_date: date | None = None) -> List[Dict[str, Any]]:
        """Return per-hour detection counts for a given date (default: today)"""
        if target_date is None:
            target_date = datetime.utcnow().date()
        start = datetime.combine(target_date, datetime.min.time())
        end = start + timedelta(days=1)
        stmt = (
            select(
                func.strftime("%H", PlateRecord.created_at).label("hour"),
                func.count(PlateRecord.id).label("total"),
            )
            .where(PlateRecord.created_at >= start, PlateRecord.created_at < end)
            .group_by(func.strftime("%H", PlateRecord.created_at))
            .order_by(func.strftime("%H", PlateRecord.created_at))
        )
        result = await self.db.execute(stmt)
        rows = result.fetchall()
        return [{"hour": int(row.hour), "total": row.total} for row in rows]

    # ------------------------------------------------------------------
    # Distributions
    # ------------------------------------------------------------------

    async def get_plate_type_distribution(self) -> Dict[str, int]:
        """Return count per plate type"""
        stmt = (
            select(PlateRecord.plate_type, func.count(PlateRecord.id).label("count"))
            .group_by(PlateRecord.plate_type)
        )
        result = await self.db.execute(stmt)
        return {row.plate_type: row.count for row in result.fetchall()}

    async def get_province_distribution(self) -> Dict[str, int]:
        """Return count per province"""
        stmt = (
            select(PlateRecord.province, func.count(PlateRecord.id).label("count"))
            .where(PlateRecord.province.isnot(None))
            .group_by(PlateRecord.province)
            .order_by(func.count(PlateRecord.id).desc())
        )
        result = await self.db.execute(stmt)
        return {row.province: row.count for row in result.fetchall()}

    async def get_confidence_histogram(self, bins: int = 10) -> List[Dict[str, Any]]:
        """Return confidence score distribution in `bins` equal-width buckets"""
        stmt = select(PlateRecord.confidence)
        result = await self.db.execute(stmt)
        values = [row[0] for row in result.fetchall() if row[0] is not None]
        if not values:
            return []
        min_v, max_v = min(values), max(values)
        width = (max_v - min_v) / bins if max_v != min_v else 1
        histogram = [0] * bins
        for v in values:
            idx = min(int((v - min_v) / width), bins - 1)
            histogram[idx] += 1
        return [
            {
                "range_start": round(min_v + i * width, 3),
                "range_end": round(min_v + (i + 1) * width, 3),
                "count": histogram[i],
            }
            for i in range(bins)
        ]

    async def get_processing_time_stats(self) -> Dict[str, Any]:
        """Return min / max / avg processing time statistics"""
        stmt = select(
            func.min(PlateRecord.processing_time).label("min"),
            func.max(PlateRecord.processing_time).label("max"),
            func.avg(PlateRecord.processing_time).label("avg"),
            func.count(PlateRecord.id).label("count"),
        )
        result = await self.db.execute(stmt)
        row = result.fetchone()
        if row is None or row.count == 0:
            return {"min": 0, "max": 0, "avg": 0, "count": 0}
        return {
            "min": round(float(row.min or 0), 4),
            "max": round(float(row.max or 0), 4),
            "avg": round(float(row.avg or 0), 4),
            "count": row.count,
        }

    # ------------------------------------------------------------------
    # Write-side: update daily stats row
    # ------------------------------------------------------------------

    async def update_daily_stats(self, detection_data: Dict[str, Any]) -> None:
        """Upsert the SystemStats row for today with incremented counters"""
        today = datetime.utcnow().date()
        stmt = select(SystemStats).where(SystemStats.date == today)
        result = await self.db.execute(stmt)
        stats = result.scalar_one_or_none()

        success = detection_data.get("is_valid", True)
        confidence = float(detection_data.get("confidence", 0))
        proc_time = float(detection_data.get("processing_time", 0))

        if stats is None:
            stats = SystemStats(
                date=today,
                total_detections=1,
                successful_detections=1 if success else 0,
                failed_detections=0 if success else 1,
                avg_confidence=confidence,
                avg_processing_time=proc_time,
                updated_at=datetime.utcnow(),
            )
            self.db.add(stats)
        else:
            total = stats.total_detections + 1
            stats.total_detections = total
            if success:
                stats.successful_detections += 1
            else:
                stats.failed_detections += 1
            # Running average
            stats.avg_confidence = (
                stats.avg_confidence * (total - 1) + confidence
            ) / total
            stats.avg_processing_time = (
                stats.avg_processing_time * (total - 1) + proc_time
            ) / total
            stats.updated_at = datetime.utcnow()

        try:
            await self.db.commit()
        except Exception as exc:
            await self.db.rollback()
            logger.error(f"Failed to update daily stats: {exc}")
