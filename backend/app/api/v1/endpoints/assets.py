from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.models import Asset
from app.schemas.schemas import AssetCreate, AssetResponse
from app.core.logging import get_logger

router = APIRouter(prefix="/assets", tags=["assets"])
logger = get_logger(__name__)


@router.post("", response_model=AssetResponse, status_code=201)
async def create_asset(
    payload: AssetCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    asset = Asset(
        owner_id=user_id,
        name=payload.name,
        asset_type=payload.asset_type,
        location_name=payload.location_name,
        latitude=payload.latitude,
        longitude=payload.longitude,
        description=payload.description,
        metadata=payload.metadata,
    )
    db.add(asset)
    await db.flush()
    await db.refresh(asset)
    logger.info("asset_created", asset_id=asset.id, owner_id=user_id)
    return asset


@router.get("", response_model=list[AssetResponse])
async def list_assets(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(
        select(Asset).where(Asset.owner_id == user_id).order_by(Asset.risk_score.desc())
    )
    return result.scalars().all()


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    asset = await db.scalar(select(Asset).where(Asset.id == asset_id, Asset.owner_id == user_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    asset = await db.scalar(select(Asset).where(Asset.id == asset_id, Asset.owner_id == user_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    await db.delete(asset)
