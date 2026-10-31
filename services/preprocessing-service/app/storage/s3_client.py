"""
Object Storage Client (MinIO / S3 Adapter).
Handles downloading raw datasets and persisting processed Parquet & metadata artifacts.
Supports local filesystem fallback for development and testing.
"""
from pathlib import Path
from typing import Optional
import os
import shutil
import urllib3
from minio import Minio
from minio.error import S3Error
from app.config.settings import settings
from app.config.logger import get_logger
from app.core.exceptions import StorageError

logger = get_logger(__name__)


class ObjectStorageClient:
    """Client for reading from raw bucket and writing to processed bucket."""
    
    def __init__(self):
        self.endpoint = settings.S3_ENDPOINT
        self.access_key = settings.S3_ACCESS_KEY
        self.secret_key = settings.S3_SECRET_KEY
        self.secure = settings.S3_USE_SSL
        self.raw_bucket = settings.S3_BUCKET_RAW
        self.processed_bucket = settings.S3_BUCKET_PROCESSED
        self._client: Optional[Minio] = None

    @property
    def client(self) -> Minio:
        if self._client is None:
            # Configure fast 1.5s connect timeout to prevent blocking when MinIO is offline in local dev/test
            http_client = urllib3.PoolManager(
                timeout=urllib3.Timeout(connect=1.5, read=10.0),
                retries=urllib3.Retry(total=1, connect=1)
            )
            self._client = Minio(
                endpoint=self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure,
                http_client=http_client
            )
        return self._client

    def download_file(self, source_uri: str, destination_path: Path) -> Path:
        """
        Downloads a dataset from S3 or local path to the specified destination.
        Handles s3://, file:// or relative paths.
        """
        try:
            if source_uri.startswith("s3://") or source_uri.startswith("minio://"):
                # Format: s3://bucket-name/path/to/file.ext
                clean_uri = source_uri.replace("s3://", "").replace("minio://", "")
                parts = clean_uri.split("/", 1)
                bucket_name = parts[0]
                object_name = parts[1] if len(parts) > 1 else ""

                destination_path.parent.mkdir(parents=True, exist_ok=True)
                self.client.fget_object(bucket_name, object_name, str(destination_path))
                logger.info(f"Downloaded S3 object {source_uri} to {destination_path}")
                return destination_path
            
            # Local filesystem source
            clean_path = source_uri.replace("file://", "")
            source_file = Path(clean_path)
            if not source_file.exists():
                raise StorageError(f"Local source dataset file not found: {source_file}")

            destination_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_file, destination_path)
            logger.info(f"Copied local file from {source_file} to {destination_path}")
            return destination_path

        except Exception as e:
            if isinstance(e, StorageError):
                raise
            raise StorageError(f"Failed to download source dataset from {source_uri}: {e}")

    def upload_file(self, local_path: Path, object_key: str, bucket_name: Optional[str] = None) -> str:
        """
        Uploads a processed artifact to S3/MinIO.
        Returns the canonical S3 URI or local fallback URI.
        """
        target_bucket = bucket_name or self.processed_bucket
        if not local_path.exists():
            raise StorageError(f"File to upload does not exist: {local_path}")

        try:
            # Check or create bucket if MinIO is reachable
            if not self.client.bucket_exists(target_bucket):
                self.client.make_bucket(target_bucket)

            self.client.fput_object(
                bucket_name=target_bucket,
                object_name=object_key,
                file_path=str(local_path)
            )
            s3_uri = f"s3://{target_bucket}/{object_key}"
            logger.info(f"Uploaded {local_path} to {s3_uri}")
            return s3_uri

        except Exception as e:
            # Fallback to local storage persistence if S3 is unavailable in local dev/testing
            logger.warning(f"S3 upload failed ({e}). Storing in local fallback directory.")
            fallback_dir = Path("./tmp/processed") / target_bucket
            fallback_dir.mkdir(parents=True, exist_ok=True)
            fallback_path = fallback_dir / object_key
            fallback_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(local_path, fallback_path)
            return f"file://{fallback_path.resolve()}"


storage_client = ObjectStorageClient()
