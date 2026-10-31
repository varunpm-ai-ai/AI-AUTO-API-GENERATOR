"""
Storage Reader Client.
Retrieves processed Parquet datasets from MinIO/S3 or local storage fallback with fast timeouts.
"""
from pathlib import Path
from typing import Optional
import urllib3
import shutil
from minio import Minio
from app.config.settings import settings
from app.config.logger import get_logger
from app.core.exceptions import StorageReadError

logger = get_logger(__name__)


class S3StorageReader:
    """Reads Parquet datasets from Object Storage with local filesystem fallback."""

    def __init__(self):
        self.endpoint = settings.S3_ENDPOINT
        self.access_key = settings.S3_ACCESS_KEY
        self.secret_key = settings.S3_SECRET_KEY
        self.secure = settings.S3_USE_SSL
        self.bucket = settings.S3_BUCKET_PROCESSED
        self._client: Optional[Minio] = None

    @property
    def client(self) -> Minio:
        if self._client is None:
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

    def resolve_dataset_local_path(self, dataset_id: str, version: str = "latest") -> Path:
        """
        Resolves the local cached Parquet file path for analytical engine scanning.
        Downloads from S3 or locates in local storage fallback.
        """
        local_cache_dir = Path("./tmp/serving_cache") / dataset_id / version
        local_cache_dir.mkdir(parents=True, exist_ok=True)
        target_file = local_cache_dir / f"dataset_{dataset_id}.parquet"

        if target_file.exists():
            return target_file

        # Check local storage fallback from Preprocessing Service
        local_fallback_path = Path(f"./tmp/processed/{self.bucket}/datasets/{dataset_id}/dataset_{dataset_id}.parquet")
        if local_fallback_path.exists():
            shutil.copyfile(local_fallback_path, target_file)
            logger.info(f"Loaded dataset {dataset_id} from local preprocessing storage fallback")
            return target_file

        # Attempt download from MinIO/S3
        object_key = f"datasets/{dataset_id}/dataset_{dataset_id}.parquet"
        try:
            self.client.fget_object(self.bucket, object_key, str(target_file))
            logger.info(f"Downloaded S3 object s3://{self.bucket}/{object_key} to {target_file}")
            return target_file
        except Exception as e:
            logger.warning(f"Failed to fetch dataset {dataset_id} from S3 ({e})")
            raise StorageReadError(f"Dataset Parquet artifact for '{dataset_id}' could not be located in S3 or local storage.")


storage_reader = S3StorageReader()
