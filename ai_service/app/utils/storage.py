import os
import io
from minio import Minio
from app.utils.logging import get_logger

logger = get_logger(__name__)

BUCKET = os.environ.get("MINIO_BUCKET_INSPECTIONS", "avas-inspections")


class StorageClient:
    def __init__(self):
        self._client = None

    def _get_client(self) -> Minio:
        if self._client is None:
            self._client = Minio(
                os.environ["MINIO_ENDPOINT"],
                access_key=os.environ["MINIO_ROOT_USER"],
                secret_key=os.environ["MINIO_ROOT_PASSWORD"],
                secure=os.environ.get("MINIO_USE_SSL", "false").lower() == "true",
            )
        return self._client

    async def download_image(self, key: str) -> bytes:
        client = self._get_client()
        try:
            response = client.get_object(BUCKET, key)
            data = response.read()
            return data
        except Exception as e:
            logger.error("storage_download_failed", key=key, error=str(e))
            raise
        finally:
            try:
                response.close()
                response.release_conn()
            except Exception:
                pass


storage_client = StorageClient()
