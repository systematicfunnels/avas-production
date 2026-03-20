import asyncio
from typing import List, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class AIServiceClient:
    """Client for communicating with the AI analysis microservice."""

    def __init__(self):
        self.base_url = settings.AI_SERVICE_URL
        self.timeout = settings.AI_INFERENCE_TIMEOUT

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.TimeoutException),
    )
    async def analyze_inspection(
        self,
        inspection_id: str,
        image_keys: List[str],
        asset_type: Optional[str] = None,
    ) -> dict:
        """
        Send inspection images to AI service for analysis.
        Returns structured defect detection results.
        """
        payload = {
            "inspection_id": inspection_id,
            "image_keys": image_keys,
            "asset_type": asset_type,
            "confidence_threshold": settings.AI_CONFIDENCE_THRESHOLD,
        }

        logger.info("ai_analysis_started", inspection_id=inspection_id, image_count=len(image_keys))

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/analyze",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                logger.info(
                    "ai_analysis_completed",
                    inspection_id=inspection_id,
                    defect_count=len(result.get("defects", [])),
                    risk_score=result.get("risk_score"),
                )
                return result

        except httpx.TimeoutException:
            logger.error("ai_analysis_timeout", inspection_id=inspection_id)
            raise
        except httpx.HTTPStatusError as e:
            logger.error("ai_analysis_http_error", inspection_id=inspection_id, status=e.response.status_code)
            raise
        except Exception as e:
            logger.error("ai_analysis_failed", inspection_id=inspection_id, error=str(e))
            raise

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False


ai_client = AIServiceClient()
