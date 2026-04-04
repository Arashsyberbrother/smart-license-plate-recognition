"""
Health check router
مسیر بررسی سلامت سرویس
"""

import time
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.schemas import HealthResponse

router = APIRouter()

_START_TIME = time.time()


@router.get("", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Return service health status including DB connectivity"""
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    overall = "healthy" if db_status == "healthy" else "unhealthy"

    return HealthResponse(
        status=overall,
        version=settings.APP_VERSION,
        database=db_status,
        uptime=round(time.time() - _START_TIME, 2),
        timestamp=datetime.utcnow().isoformat(),
    )
