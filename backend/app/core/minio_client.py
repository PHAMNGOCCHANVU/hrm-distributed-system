import io
import uuid
import logging
from typing import Optional
from minio import Minio
from minio.error import S3Error

from app.core.config import settings

logger = logging.getLogger("minio_client")

# Khởi tạo MinIO Client
minio_client = Minio(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE
)


def ensure_bucket_exists():
    """Đảm bảo bucket đã tồn tại trên MinIO."""
    try:
        if not minio_client.bucket_exists(settings.MINIO_BUCKET):
            minio_client.make_bucket(settings.MINIO_BUCKET)
            logger.info(f"Created bucket {settings.MINIO_BUCKET} successfully.")
    except Exception as e:
        logger.error(f"Error checking/creating MinIO bucket: {e}")


# Đảm bảo bucket sẵn sàng khi nạp module
try:
    ensure_bucket_exists()
except Exception as e:
    logger.warning(f"MinIO server not available during startup: {e}")


def upload_file(
    file_bytes: bytes,
    original_filename: str,
    folder: str = "avatars",
    content_type: str = "application/octet-stream"
) -> str:
    """
    Tải file nhị phân lên MinIO S3 bucket.
    Trả về: object_key duy nhất có định dạng {folder}/{uuid}_{filename}.
    """
    clean_filename = original_filename.replace(" ", "_")
    unique_suffix = uuid.uuid4().hex[:8]
    object_key = f"{folder}/{unique_suffix}_{clean_filename}"

    file_stream = io.BytesIO(file_bytes)
    file_length = len(file_bytes)

    minio_client.put_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=object_key,
        data=file_stream,
        length=file_length,
        content_type=content_type
    )
    logger.info(f"Uploaded file to MinIO: {object_key}")
    return object_key


def delete_file(object_key: str) -> bool:
    """
    Xóa đối tượng khỏi MinIO bucket phục vụ cơ chế đền bù (Compensating Transaction) khi ghi CSDL thất bại.
    """
    if not object_key:
        return True
    try:
        minio_client.remove_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_key
        )
        logger.info(f"Deleted file from MinIO: {object_key}")
        return True
    except S3Error as e:
        logger.error(f"Failed to delete file from MinIO {object_key}: {e}")
        return False


def get_public_url(object_key: Optional[str]) -> Optional[str]:
    """
    Tạo URL truy cập công khai trực tiếp tới tệp trên MinIO S3.
    """
    if not object_key:
        return None
    if object_key.startswith("http://") or object_key.startswith("https://"):
        return object_key
    return f"http://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET}/{object_key}"
