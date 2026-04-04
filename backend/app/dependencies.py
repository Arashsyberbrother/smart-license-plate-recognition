"""
Shared FastAPI dependencies
وابستگی‌های مشترک FastAPI
"""

from fastapi import Header, HTTPException, Query, status
from typing import Optional

from app.config import settings
from app.database import get_db  # re-export for convenience

__all__ = ["get_db", "get_current_api_key", "PaginationParams"]


async def get_current_api_key(x_api_key: Optional[str] = Header(default=None)) -> Optional[str]:
    """
    Optional API key validation.
    If API_KEY is configured in settings, all requests must supply a matching key.
    """
    if not settings.API_KEY:
        return None
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return x_api_key


class PaginationParams:
    """Reusable query-parameter-based pagination"""

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Page number"),
        per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    ) -> None:
        self.page = page
        self.per_page = per_page

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page
