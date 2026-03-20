from contextlib import asynccontextmanager
from typing import List, Optional
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.models.defect_detection import defect_model
from app.models.risk_scoring import risk_model
from app.processors.image_processor import image_processor
from app.utils.logging import setup_logging, get_logger
from app.utils.storage import storage_client

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ai_service_startup")
    defect_model.load()
    logger.info("ai_service_ready")
    yield
    logger.info("ai_service_shutdown")


app = FastAPI(title="AVAS AI Service", version="1.0.0", lifespan=lifespan)


class AnalyzeRequest(BaseModel):
    inspection_id: str
    image_keys: List[str]
    asset_type: Optional[str] = None
    confidence_threshold: float = 0.5


class AnalyzeResponse(BaseModel):
    inspection_id: str
    defects: List[dict]
    risk_score: float
    maintenance_priority: str
    summary: str
    images_processed: int
    images_failed: int


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model_loaded": defect_model.is_loaded(),
    }


@app.post("/v1/analyze", response_model=AnalyzeResponse)
async def analyze_inspection(request: AnalyzeRequest):
    if not defect_model.is_loaded():
        raise HTTPException(status_code=503, detail="AI model not ready")

    if not request.image_keys:
        raise HTTPException(status_code=400, detail="No images provided")

    if len(request.image_keys) > 200:
        raise HTTPException(status_code=400, detail="Maximum 200 images per inspection")

    logger.info(
        "analysis_started",
        inspection_id=request.inspection_id,
        image_count=len(request.image_keys),
    )

    all_defects = []
    images_processed = 0
    images_failed = 0

    # Process images in batches to control memory usage
    batch_size = 8
    for i in range(0, len(request.image_keys), batch_size):
        batch = request.image_keys[i:i + batch_size]
        batch_results = await asyncio.gather(
            *[_process_single_image(key, request.confidence_threshold) for key in batch],
            return_exceptions=True,
        )
        for key, result in zip(batch, batch_results):
            if isinstance(result, Exception):
                logger.warning("image_processing_failed", key=key, error=str(result))
                images_failed += 1
            else:
                all_defects.extend(result)
                images_processed += 1

    risk_score = risk_model.compute_risk_score(all_defects)
    priority = risk_model.generate_maintenance_priority(risk_score)
    summary = risk_model.generate_summary(all_defects, risk_score)

    logger.info(
        "analysis_completed",
        inspection_id=request.inspection_id,
        defect_count=len(all_defects),
        risk_score=risk_score,
    )

    return AnalyzeResponse(
        inspection_id=request.inspection_id,
        defects=all_defects,
        risk_score=risk_score,
        maintenance_priority=priority,
        summary=summary,
        images_processed=images_processed,
        images_failed=images_failed,
    )


async def _process_single_image(image_key: str, confidence_threshold: float) -> List[dict]:
    """Download image from storage and run defect detection."""
    image_data = await storage_client.download_image(image_key)
    original, preprocessed = image_processor.preprocess(image_data)
    detections = defect_model.predict(preprocessed, confidence_threshold, image_key=image_key)
    return detections
