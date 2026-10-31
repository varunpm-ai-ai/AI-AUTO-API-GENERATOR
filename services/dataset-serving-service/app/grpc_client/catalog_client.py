"""
Dataset Catalog gRPC Client.
Provides high-performance, binary RPC communication with Dataset Catalog Service (Port 50053).
Includes timeout guards and graceful degradation fallbacks.
"""
from typing import Optional, List, Dict, Any
import grpc
from app.grpc_client.dataset_catalog_pb2_grpc import DatasetCatalogServiceStub
from app.grpc_client import dataset_catalog_pb2 as pb
from app.config.settings import settings
from app.config.logger import get_logger

logger = get_logger(__name__)


class CatalogGrpcClient:
    """Synchronous binary gRPC client for Catalog Service control-plane operations."""

    def __init__(self, target: Optional[str] = None):
        self.target = target or f"{settings.CATALOG_GRPC_HOST}:{settings.CATALOG_GRPC_PORT}"
        self._channel: Optional[grpc.Channel] = None
        self._stub: Optional[DatasetCatalogServiceStub] = None

    def _get_stub(self) -> DatasetCatalogServiceStub:
        if self._channel is None:
            # Configure gRPC keepalive and timeout options
            options = [
                ("grpc.keepalive_time_ms", 10000),
                ("grpc.keepalive_timeout_ms", 5000),
                ("grpc.keepalive_permit_without_calls", True),
                ("grpc.http2.max_pings_without_data", 0),
            ]
            self._channel = grpc.insecure_channel(self.target, options=options)
            self._stub = DatasetCatalogServiceStub(self._channel)
        return self._stub

    def get_dataset(self, dataset_id: str, timeout: float = 2.0) -> Optional[pb.DatasetDetailResponse]:
        """Fetches dataset metadata and version details from Catalog Service via gRPC."""
        try:
            stub = self._get_stub()
            req = pb.GetDatasetRequest(dataset_id=dataset_id)
            response = stub.GetDataset(req, timeout=timeout)
            logger.info(f"[gRPC] Retrieved dataset details for '{dataset_id}' from Catalog Service")
            return response
        except grpc.RpcError as e:
            logger.warning(f"[gRPC] Failed to get dataset '{dataset_id}' via gRPC ({e.code()}): {e.details()}")
            return None

    def list_datasets(self, page: int = 1, limit: int = 50, timeout: float = 2.0) -> Optional[pb.ListDatasetsResponse]:
        """Lists registered datasets from Catalog Service via gRPC."""
        try:
            stub = self._get_stub()
            req = pb.ListDatasetsRequest(page=page, limit=limit)
            response = stub.ListDatasets(req, timeout=timeout)
            logger.info(f"[gRPC] Retrieved {len(response.datasets)} datasets from Catalog Service")
            return response
        except grpc.RpcError as e:
            logger.warning(f"[gRPC] Failed to list datasets via gRPC ({e.code()}): {e.details()}")
            return None

    def get_version_status(self, dataset_id: str, version_id: str, timeout: float = 2.0) -> Optional[pb.VersionStatusResponse]:
        """Inspects dataset version status and history via gRPC."""
        try:
            stub = self._get_stub()
            req = pb.GetVersionStatusRequest(dataset_id=dataset_id, version_id=version_id)
            response = stub.GetVersionStatus(req, timeout=timeout)
            return response
        except grpc.RpcError as e:
            logger.warning(f"[gRPC] Failed to get version status for '{dataset_id}' ({e.code()}): {e.details()}")
            return None

    def check_duplicate(self, checksum: str, storage_ref: str, timeout: float = 2.0) -> Optional[pb.CheckDuplicateResponse]:
        """Checks for existing duplicates in catalog via gRPC."""
        try:
            stub = self._get_stub()
            req = pb.CheckDuplicateRequest(checksum=checksum, storage_ref=storage_ref)
            response = stub.CheckDuplicate(req, timeout=timeout)
            return response
        except grpc.RpcError as e:
            logger.warning(f"[gRPC] Failed to check duplicate ({e.code()}): {e.details()}")
            return None

    def close(self):
        if self._channel:
            self._channel.close()
            self._channel = None
            self._stub = None


catalog_grpc_client = CatalogGrpcClient()
