from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.models import Inspection, Asset, Defect, InspectionStatus, DefectSeverity
from app.schemas.schemas import DashboardStats, RiskSummary
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnalyticsService:

    async def get_dashboard_stats(self, db: AsyncSession, owner_id: str) -> DashboardStats:
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        total_inspections = await db.scalar(
            select(func.count(Inspection.id)).where(Inspection.owner_id == owner_id)
        ) or 0

        total_assets = await db.scalar(
            select(func.count(Asset.id)).where(Asset.owner_id == owner_id)
        ) or 0

        defect_query = (
            select(func.count(Defect.id))
            .join(Inspection, Defect.inspection_id == Inspection.id)
            .where(Inspection.owner_id == owner_id)
        )
        total_defects = await db.scalar(defect_query) or 0

        critical_defects = await db.scalar(
            defect_query.where(Defect.severity == DefectSeverity.CRITICAL)
        ) or 0

        avg_risk = await db.scalar(
            select(func.avg(Inspection.risk_score)).where(
                Inspection.owner_id == owner_id,
                Inspection.risk_score.isnot(None),
            )
        ) or 0.0

        inspections_this_month = await db.scalar(
            select(func.count(Inspection.id)).where(
                Inspection.owner_id == owner_id,
                Inspection.created_at >= month_start,
            )
        ) or 0

        return DashboardStats(
            total_inspections=total_inspections,
            total_assets=total_assets,
            total_defects=total_defects,
            critical_defects=critical_defects,
            avg_risk_score=round(float(avg_risk), 2),
            inspections_this_month=inspections_this_month,
        )

    async def get_risk_summary(self, db: AsyncSession, owner_id: str) -> list[RiskSummary]:
        result = await db.execute(
            select(Asset)
            .where(Asset.owner_id == owner_id)
            .order_by(Asset.risk_score.desc())
            .limit(20)
        )
        assets = result.scalars().all()

        summaries = []
        for asset in assets:
            last_inspection = await db.scalar(
                select(func.max(Inspection.completed_at)).where(
                    Inspection.asset_id == asset.id,
                    Inspection.status == InspectionStatus.COMPLETED,
                )
            )
            defect_count = await db.scalar(
                select(func.count(Defect.id))
                .join(Inspection, Defect.inspection_id == Inspection.id)
                .where(Inspection.asset_id == asset.id)
            ) or 0

            summaries.append(RiskSummary(
                asset_id=asset.id,
                asset_name=asset.name,
                risk_score=asset.risk_score,
                defect_count=defect_count,
                last_inspection=last_inspection,
            ))

        return summaries


analytics_service = AnalyticsService()
