import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.ai.inspection_service import inspection_service
from app.services.storage.storage_service import storage_service
from app.schemas.schemas import InspectionCreate, InspectionResponse, InspectionListResponse, PaginatedResponse
from app.core.config import get_settings
from app.core.logging import get_logger
import math

router = APIRouter(prefix="/inspections", tags=["inspections"])
logger = get_logger(__name__)
settings = get_settings()


@router.post("", response_model=InspectionResponse, status_code=201)
async def create_inspection(
    payload: InspectionCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    inspection = await inspection_service.create_inspection(
        db=db,
        owner_id=user_id,
        title=payload.title,
        asset_id=payload.asset_id,
    )
    return inspection


@router.post("/{inspection_id}/upload")
async def upload_images(
    inspection_id: str,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 images per upload")

    from sqlalchemy import select
    from app.models.models import Inspection, InspectionStatus
    inspection = await db.scalar(
        select(Inspection).where(Inspection.id == inspection_id, Inspection.owner_id == user_id)
    )
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    if inspection.status == InspectionStatus.PROCESSING:
        raise HTTPException(status_code=409, detail="Cannot upload images while processing")

    uploaded_keys = []
    errors = []

    for file in files:
        try:
            content_type = file.content_type or "application/octet-stream"
            file_data = await file.read()
            storage_service.validate_image(content_type, len(file_data), file.filename or "unknown")
            key = await storage_service.upload_inspection_image(
                inspection_id=inspection_id,
                file_data=file_data,
                content_type=content_type,
                original_filename=file.filename or "image",
            )
            uploaded_keys.append(key)
        except ValueError as e:
            errors.append({"file": file.filename, "error": str(e)})
        except Exception as e:
            logger.error("upload_failed", filename=file.filename, error=str(e))
            errors.append({"file": file.filename, "error": "Upload failed"})

    if uploaded_keys:
        await inspection_service.add_images(db, inspection, uploaded_keys)

    return {
        "uploaded": len(uploaded_keys),
        "failed": len(errors),
        "errors": errors,
        "total_images": inspection.image_count,
    }


@router.post("/{inspection_id}/analyze")
async def analyze_inspection(
    inspection_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    from sqlalchemy import select
    from app.models.models import Inspection
    inspection = await db.scalar(
        select(Inspection).where(Inspection.id == inspection_id, Inspection.owner_id == user_id)
    )
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")

    asset_type = None
    if inspection.asset_id:
        from app.models.models import Asset
        asset = await db.scalar(select(Asset).where(Asset.id == inspection.asset_id))
        if asset:
            asset_type = asset.asset_type

    # Run AI processing as background task for non-blocking response
    background_tasks.add_task(
        _run_analysis_background,
        inspection_id=inspection_id,
        asset_type=asset_type,
    )

    return {"message": "Analysis started", "inspection_id": inspection_id, "status": "processing"}


async def _run_analysis_background(inspection_id: str, asset_type: Optional[str]):
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        try:
            await inspection_service.process_inspection(db, inspection_id, asset_type)
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error("background_analysis_failed", inspection_id=inspection_id, error=str(e))


@router.get("", response_model=PaginatedResponse)
async def list_inspections(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    items, total = await inspection_service.get_inspections(db, user_id, page, page_size)
    return PaginatedResponse(
        items=[InspectionListResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.get("/{inspection_id}", response_model=InspectionResponse)
async def get_inspection(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    inspection = await inspection_service.get_inspection_detail(db, inspection_id, user_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection
