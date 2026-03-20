from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.analytics.analytics_service import analytics_service
from app.schemas.schemas import DashboardStats, RiskSummary
from typing import List

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardStats)
async def dashboard_stats(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    return await analytics_service.get_dashboard_stats(db, user_id)


@router.get("/risk-summary", response_model=List[RiskSummary])
async def risk_summary(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    return await analytics_service.get_risk_summary(db, user_id)
