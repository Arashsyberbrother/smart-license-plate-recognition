"""
Plate detection and management endpoints
مسیرهای تشخیص و مدیریت پلاک
"""

from __future__ import annotations

import base64
import io
import logging
import math
import os
import time
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import PaginationParams
from app.models import PlateRecord
from app.schemas import (
    PlateDetectionRequest,
    PlateDetectionResponse,
    PlateListResponse,
    PlateRecordCreate,
    PlateRecordResponse,
)
from services.ocr_service import get_ocr_service
from services.plate_detector import get_plate_detector
from services.validation import IranianPlateValidator

logger = logging.getLogger(__name__)

router = APIRouter()
validator = IranianPlateValidator()


# ---------------------------------------------------------------------------
# Helper: run the full detection pipeline on raw image bytes
# ---------------------------------------------------------------------------

async def _run_pipeline(image_bytes: bytes) -> dict:
    """
    Orchestrate detector → OCR → validation → return result dict.
    Saves annotated image to uploads/ and returns its path.
    """
    start = time.time()

    detector = get_plate_detector(
        model_path=settings.MODEL_PATH,
        confidence_threshold=settings.CONFIDENCE_THRESHOLD,
    )
    ocr_svc = get_ocr_service()

    # 1. Detect bounding boxes
    detections = detector.detect(image_bytes)
    if not detections:
        return {
            "plate_number": "UNKNOWN",
            "plate_type": "unknown",
            "province": None,
            "confidence": 0.0,
            "is_valid": False,
            "vehicle_type": None,
            "processing_time": time.time() - start,
            "raw_text": None,
            "image_path": None,
            "message": "No plate detected in image",
        }

    best = max(detections, key=lambda d: d["confidence"])

    # 2. OCR
    try:
        from PIL import Image

        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        pil_image = None

    ocr_result = ocr_svc.read_plate(pil_image, bbox=tuple(best["bbox"]))

    # 3. Validate
    plate_text = ocr_result.get("text", "")
    validation = validator.validate(plate_text)

    # 4. Save annotated image
    image_path: Optional[str] = None
    try:
        annotated = detector.draw_detections(image_bytes, detections)
        if annotated:
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            filename = f"{uuid.uuid4().hex}.png"
            full_path = os.path.join(settings.UPLOAD_DIR, filename)
            with open(full_path, "wb") as f:
                f.write(annotated)
            image_path = f"/uploads/{filename}"
    except Exception as exc:
        logger.warning(f"Could not save annotated image: {exc}")

    processing_time = time.time() - start

    return {
        "plate_number": validation.get("formatted") or plate_text or "UNKNOWN",
        "plate_type": validation.get("plate_type", "unknown"),
        "province": validation.get("province"),
        "confidence": best["confidence"],
        "is_valid": validation.get("is_valid", False),
        "vehicle_type": None,
        "processing_time": round(processing_time, 4),
        "raw_text": ocr_result.get("raw_text"),
        "image_path": image_path,
        "message": validation.get("message", "Detection complete"),
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/detect", response_model=PlateDetectionResponse, status_code=status.HTTP_200_OK)
async def detect_plate(
    file: Optional[UploadFile] = File(default=None),
    body: Optional[PlateDetectionRequest] = None,
    db: AsyncSession = Depends(get_db),
) -> PlateDetectionResponse:
    """
    Detect an Iranian license plate.
    Accepts either a multipart file upload or a JSON body with base64 image.
    """
    image_bytes: Optional[bytes] = None

    if file is not None:
        if file.content_type and not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Uploaded file must be an image",
            )
        image_bytes = await file.read()
        if len(image_bytes) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image size exceeds maximum allowed",
            )
    elif body is not None:
        try:
            # Strip data URI prefix if present
            b64 = body.image.split(",")[-1]
            image_bytes = base64.b64decode(b64)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid base64 image data",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide either a file upload or a JSON body with base64 image",
        )

    result = await _run_pipeline(image_bytes)

    # Persist to database
    try:
        record = PlateRecord(
            plate_number=result["plate_number"],
            plate_type=result["plate_type"],
            province=result["province"],
            confidence=result["confidence"],
            image_path=result["image_path"],
            raw_text=result["raw_text"],
            is_valid=result["is_valid"],
            vehicle_type=result["vehicle_type"],
            processing_time=result["processing_time"],
        )
        db.add(record)
        await db.commit()
    except Exception as exc:
        logger.error(f"DB persist error: {exc}")
        await db.rollback()

    return PlateDetectionResponse(**result)


@router.get("", response_model=PlateListResponse)
async def list_plates(
    pagination: PaginationParams = Depends(),
    plate_number: Optional[str] = Query(default=None),
    plate_type: Optional[str] = Query(default=None),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PlateListResponse:
    """List plate records with optional filters and pagination"""
    stmt = select(PlateRecord)

    if plate_number:
        stmt = stmt.where(PlateRecord.plate_number.contains(plate_number))
    if plate_type:
        stmt = stmt.where(PlateRecord.plate_type == plate_type)
    if date_from:
        try:
            stmt = stmt.where(
                PlateRecord.created_at >= datetime.fromisoformat(date_from)
            )
        except ValueError:
            pass
    if date_to:
        try:
            stmt = stmt.where(
                PlateRecord.created_at <= datetime.fromisoformat(date_to)
            )
        except ValueError:
            pass

    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one() or 0

    # Paginate
    stmt = (
        stmt.order_by(PlateRecord.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.per_page)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()

    pages = math.ceil(total / pagination.per_page) if total else 0

    return PlateListResponse(
        items=[PlateRecordResponse.model_validate(item) for item in items],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=pages,
    )


@router.get("/search/{query}", response_model=PlateListResponse)
async def search_plates(
    query: str,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PlateListResponse:
    """Full-text search on plate_number and province"""
    stmt = select(PlateRecord).where(
        or_(
            PlateRecord.plate_number.contains(query),
            PlateRecord.province.contains(query),
        )
    )
    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one() or 0

    stmt = (
        stmt.order_by(PlateRecord.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.per_page)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()
    pages = math.ceil(total / pagination.per_page) if total else 0

    return PlateListResponse(
        items=[PlateRecordResponse.model_validate(item) for item in items],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=pages,
    )


@router.get("/{plate_id}", response_model=PlateRecordResponse)
async def get_plate(
    plate_id: int,
    db: AsyncSession = Depends(get_db),
) -> PlateRecordResponse:
    """Retrieve a single plate record by ID"""
    result = await db.execute(select(PlateRecord).where(PlateRecord.id == plate_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plate record not found")
    return PlateRecordResponse.model_validate(record)


@router.delete("/{plate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plate(
    plate_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a plate record by ID"""
    result = await db.execute(select(PlateRecord).where(PlateRecord.id == plate_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plate record not found")
    await db.delete(record)
    await db.commit()
