import io
import uuid
from typing import Optional
from minio import Minio
from minio.error import S3Error
from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/tiff", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp"}


class StorageService:
    def __init__(self):
        self._client: Optional[Minio] = None

    def _get_client(self) -> Minio:
        if self._client is None:
            self._client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ROOT_USER,
                secret_key=settings.MINIO_ROOT_PASSWORD,
                secure=settings.MINIO_USE_SSL,
            )
        return self._client

    async def ensure_buckets(self):
        client = self._get_client()
        for bucket in [settings.MINIO_BUCKET_INSPECTIONS, settings.MINIO_BUCKET_RESULTS]:
            try:
                if not client.bucket_exists(bucket):
                    client.make_bucket(bucket)
                    logger.info("bucket_created", bucket=bucket)
            except S3Error as e:
                logger.error("bucket_creation_failed", bucket=bucket, error=str(e))
                raise

    def validate_image(self, content_type: str, file_size: int, filename: str) -> None:
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise ValueError(f"Invalid file type: {content_type}. Allowed: {ALLOWED_IMAGE_TYPES}")
        if file_size > settings.max_image_bytes:
            raise ValueError(f"File too large: {file_size} bytes. Max: {settings.max_image_bytes} bytes")
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Invalid extension: {ext}")

    async def upload_inspection_image(
        self,
        inspection_id: str,
        file_data: bytes,
        content_type: str,
        original_filename: str,
    ) -> str:
        key = f"{inspection_id}/{uuid.uuid4()}-{original_filename}"
        client = self._get_client()
        try:
            client.put_object(
                settings.MINIO_BUCKET_INSPECTIONS,
                key,
                io.BytesIO(file_data),
                length=len(file_data),
                content_type=content_type,
            )
            logger.info("image_uploaded", key=key, size=len(file_data))
            return key
        except S3Error as e:
            logger.error("image_upload_failed", key=key, error=str(e))
            raise

    async def get_presigned_url(self, bucket: str, key: str, expires_seconds: int = 3600) -> str:
        from datetime import timedelta
        client = self._get_client()
        try:
            url = client.presigned_get_object(bucket, key, expires=timedelta(seconds=expires_seconds))
            return url
        except S3Error as e:
            logger.error("presigned_url_failed", key=key, error=str(e))
            raise

    async def download_file(self, bucket: str, key: str) -> bytes:
        client = self._get_client()
        try:
            response = client.get_object(bucket, key)
            return response.read()
        except S3Error as e:
            logger.error("file_download_failed", key=key, error=str(e))
            raise
        finally:
            response.close()
            response.release_conn()

    async def delete_file(self, bucket: str, key: str) -> None:
        client = self._get_client()
        try:
            client.remove_object(bucket, key)
        except S3Error as e:
            logger.error("file_delete_failed", key=key, error=str(e))


storage_service = StorageService()
