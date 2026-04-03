"""
Dashboard statistics router
مسیرهای آمار داشبورد
"""

from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import PlateRecord
from app.schemas import DashboardStats

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_stats(db: AsyncSession = Depends(get_db)) -> DashboardStats:
    """Return aggregated dashboard statistics"""

    # Total detections
    total_stmt = select(func.count(PlateRecord.id))
    total_result = await db.execute(total_stmt)
    total_detections = total_result.scalar_one() or 0

    # Today's detections
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_stmt = select(func.count(PlateRecord.id)).where(
        PlateRecord.created_at >= today_start
    )
    today_result = await db.execute(today_stmt)
    today_detections = today_result.scalar_one() or 0

    # Success rate
    valid_stmt = select(func.count(PlateRecord.id)).where(PlateRecord.is_valid == True)
    valid_result = await db.execute(valid_stmt)
    valid_count = valid_result.scalar_one() or 0
    success_rate = round((valid_count / total_detections * 100) if total_detections else 0.0, 2)

    # Avg confidence and processing time
    agg_stmt = select(
        func.avg(PlateRecord.confidence).label("avg_conf"),
        func.avg(PlateRecord.processing_time).label("avg_proc"),
    )
    agg_result = await db.execute(agg_stmt)
    agg_row = agg_result.fetchone()
    avg_confidence = round(float(agg_row.avg_conf or 0), 4)
    avg_processing_time = round(float(agg_row.avg_proc or 0), 4)

    # Recent plates (last 10)
    recent_stmt = (
        select(PlateRecord)
        .order_by(PlateRecord.created_at.desc())
        .limit(10)
    )
    recent_result = await db.execute(recent_stmt)
    recent_plates = [
        {
            "id": r.id,
            "plate_number": r.plate_number,
            "plate_type": r.plate_type,
            "province": r.province,
            "confidence": r.confidence,
            "is_valid": r.is_valid,
            "created_at": r.created_at.isoformat(),
        }
        for r in recent_result.scalars().all()
    ]

    return DashboardStats(
        total_detections=total_detections,
        today_detections=today_detections,
        success_rate=success_rate,
        avg_confidence=avg_confidence,
        avg_processing_time=avg_processing_time,
        recent_plates=recent_plates,
    )


@router.get("/recent")
async def get_recent(db: AsyncSession = Depends(get_db)):
    """Return the 10 most recent plate detections"""
    stmt = select(PlateRecord).order_by(PlateRecord.created_at.desc()).limit(10)
    result = await db.execute(stmt)
    records = result.scalars().all()
    return [
        {
            "id": r.id,
            "plate_number": r.plate_number,
            "plate_type": r.plate_type,
            "province": r.province,
            "confidence": r.confidence,
            "is_valid": r.is_valid,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]
