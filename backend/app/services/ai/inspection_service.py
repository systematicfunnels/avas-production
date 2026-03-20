import asyncio
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from app.models.models import Inspection, Defect, Asset, InspectionStatus, DefectSeverity
from app.services.ai.ai_client import ai_client
from app.core.logging import get_logger
import time

logger = get_logger(__name__)

SEVERITY_MAP = {
    "low": DefectSeverity.LOW,
    "medium": DefectSeverity.MEDIUM,
    "high": DefectSeverity.HIGH,
    "critical": DefectSeverity.CRITICAL,
}

RISK_WEIGHTS = {
    DefectSeverity.LOW: 0.1,
    DefectSeverity.MEDIUM: 0.3,
    DefectSeverity.HIGH: 0.6,
    DefectSeverity.CRITICAL: 1.0,
}


class InspectionService:

    async def create_inspection(
        self,
        db: AsyncSession,
        owner_id: str,
        title: str,
        asset_id: Optional[str] = None,
    ) -> Inspection:
        inspection = Inspection(
            owner_id=owner_id,
            asset_id=asset_id,
            title=title,
            status=InspectionStatus.PENDING,
        )
        db.add(inspection)
        await db.flush()
        await db.refresh(inspection)
        logger.info("inspection_created", inspection_id=inspection.id, owner_id=owner_id)
        return inspection

    async def add_images(
        self,
        db: AsyncSession,
        inspection: Inspection,
        storage_keys: List[str],
    ) -> Inspection:
        current_keys = inspection.storage_keys or []
        inspection.storage_keys = current_keys + storage_keys
        inspection.image_count = len(inspection.storage_keys)
        await db.flush()
        return inspection

    async def process_inspection(
        self,
        db: AsyncSession,
        inspection_id: str,
        asset_type: Optional[str] = None,
    ) -> Inspection:
        """Trigger async AI analysis for an inspection."""
        result = await db.execute(select(Inspection).where(Inspection.id == inspection_id))
        inspection = result.scalar_one_or_none()
        if not inspection:
            raise ValueError(f"Inspection {inspection_id} not found")

        if not inspection.storage_keys:
            raise ValueError("No images uploaded for this inspection")

        if inspection.status == InspectionStatus.PROCESSING:
            raise ValueError("Inspection is already being processed")

        inspection.status = InspectionStatus.PROCESSING
        await db.flush()

        start_ms = int(time.time() * 1000)

        try:
            ai_result = await ai_client.analyze_inspection(
                inspection_id=inspection_id,
                image_keys=inspection.storage_keys,
                asset_type=asset_type,
            )

            defects = await self._save_defects(db, inspection_id, ai_result.get("defects", []))
            risk_score = self._calculate_risk_score(defects)

            inspection.status = InspectionStatus.COMPLETED
            inspection.ai_result = ai_result
            inspection.risk_score = risk_score
            inspection.defect_count = len(defects)
            inspection.processing_duration_ms = int(time.time() * 1000) - start_ms
            inspection.completed_at = datetime.now(timezone.utc)

            # Update asset risk score
            if inspection.asset_id:
                await self._update_asset_risk(db, inspection.asset_id, risk_score)

            logger.info(
                "inspection_processed",
                inspection_id=inspection_id,
                defect_count=len(defects),
                risk_score=risk_score,
            )

        except Exception as e:
            inspection.status = InspectionStatus.FAILED
            inspection.error_message = str(e)
            inspection.processing_duration_ms = int(time.time() * 1000) - start_ms
            logger.error("inspection_processing_failed", inspection_id=inspection_id, error=str(e))

        await db.flush()
        return inspection

    async def _save_defects(
        self,
        db: AsyncSession,
        inspection_id: str,
        defect_data: List[dict],
    ) -> List[Defect]:
        defects = []
        for d in defect_data:
            severity_str = d.get("severity", "low").lower()
            severity = SEVERITY_MAP.get(severity_str, DefectSeverity.LOW)
            defect = Defect(
                inspection_id=inspection_id,
                defect_type=d.get("type", "unknown"),
                severity=severity,
                confidence=float(d.get("confidence", 0.0)),
                bbox=d.get("bbox"),
                image_key=d.get("image_key"),
                description=d.get("description"),
                recommendation=d.get("recommendation"),
                metadata=d.get("metadata", {}),
            )
            db.add(defect)
            defects.append(defect)
        await db.flush()
        return defects

    def _calculate_risk_score(self, defects: List[Defect]) -> float:
        if not defects:
            return 0.0
        total_weight = sum(RISK_WEIGHTS.get(d.severity, 0.1) * d.confidence for d in defects)
        max_possible = len(defects) * 1.0
        raw = min(total_weight / max_possible, 1.0) if max_possible > 0 else 0.0
        return round(raw * 100, 2)

    async def _update_asset_risk(self, db: AsyncSession, asset_id: str, new_risk: float):
        await db.execute(
            update(Asset).where(Asset.id == asset_id).values(risk_score=new_risk)
        )

    async def get_inspections(
        self,
        db: AsyncSession,
        owner_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Inspection], int]:
        offset = (page - 1) * page_size
        query = select(Inspection).where(Inspection.owner_id == owner_id).order_by(Inspection.created_at.desc())
        count_query = select(func.count()).where(Inspection.owner_id == owner_id).select_from(Inspection)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        result = await db.execute(query.offset(offset).limit(page_size))
        items = result.scalars().all()
        return list(items), total

    async def get_inspection_detail(
        self,
        db: AsyncSession,
        inspection_id: str,
        owner_id: str,
    ) -> Optional[Inspection]:
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(Inspection)
            .options(selectinload(Inspection.defects))
            .where(Inspection.id == inspection_id, Inspection.owner_id == owner_id)
        )
        return result.scalar_one_or_none()


inspection_service = InspectionService()
