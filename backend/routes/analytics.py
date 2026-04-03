"""
Analytics router
مسیرهای تحلیل آمار
"""

from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import AnalyticsResponse
from services.analytics import AnalyticsService

router = APIRouter()


@router.get("/daily", response_model=AnalyticsResponse)
async def daily_stats(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsResponse:
    """Daily detection statistics for the last N days"""
    svc = AnalyticsService(db)
    data = await svc.get_daily_stats(days)
    total = sum(row["total"] for row in data)
    return AnalyticsResponse(
        period=f"last_{days}_days",
        data=data,
        summary={"total_detections": total, "days": len(data)},
    )


@router.get("/hourly", response_model=AnalyticsResponse)
async def hourly_stats(
    date_str: str = Query(default=None, alias="date", description="Date YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsResponse:
    """Hourly detection breakdown for a specific date"""
    target: date | None = None
    if date_str:
        try:
            target = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target = None
    svc = AnalyticsService(db)
    data = await svc.get_hourly_stats(target)
    return AnalyticsResponse(
        period=str(target or datetime.utcnow().date()),
        data=data,
        summary={"total_hours_with_data": len(data)},
    )


@router.get("/distribution", response_model=AnalyticsResponse)
async def plate_type_distribution(db: AsyncSession = Depends(get_db)) -> AnalyticsResponse:
    """Plate type distribution"""
    svc = AnalyticsService(db)
    dist = await svc.get_plate_type_distribution()
    data = [{"plate_type": k, "count": v} for k, v in dist.items()]
    return AnalyticsResponse(period="all_time", data=data, summary=dist)


@router.get("/provinces", response_model=AnalyticsResponse)
async def province_distribution(db: AsyncSession = Depends(get_db)) -> AnalyticsResponse:
    """Province distribution"""
    svc = AnalyticsService(db)
    dist = await svc.get_province_distribution()
    data = [{"province": k, "count": v} for k, v in dist.items()]
    return AnalyticsResponse(period="all_time", data=data, summary={"total_provinces": len(dist)})


@router.get("/performance", response_model=AnalyticsResponse)
async def performance_stats(db: AsyncSession = Depends(get_db)) -> AnalyticsResponse:
    """Processing time and confidence performance metrics"""
    svc = AnalyticsService(db)
    proc_stats = await svc.get_processing_time_stats()
    conf_histogram = await svc.get_confidence_histogram()
    return AnalyticsResponse(
        period="all_time",
        data=conf_histogram,
        summary=proc_stats,
    )
