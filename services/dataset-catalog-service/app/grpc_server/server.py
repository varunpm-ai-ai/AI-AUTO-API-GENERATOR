import grpc
from concurrent import futures
from typing import Optional

from app.config import settings
from app.database import AsyncSessionLocal
from app.services.dataset_registration_service import dataset_registration_manager
from app.services.identity_resolution_service import identity_resolution_manager
from app.services.duplicate_detection_service import duplicate_detector
from app.services.version_service import version_manager
from app.logger import logger

# Try importing generated pb2 files if available, otherwise compile dynamically or handle gracefully
try:
    import app.grpc_server.dataset_catalog_pb2 as pb2
    import app.grpc_server.dataset_catalog_pb2_grpc as pb2_grpc
    HAS_PB2 = True
except ImportError:
    HAS_PB2 = False


class DatasetCatalogGrpcServicer:
    """gRPC Servicer for Dataset Catalog Service."""

    async def RegisterDataset(self, request, context):
        payload = {
            "name": request.name,
            "description": request.description,
            "domain": request.domain,
            "source": request.source,
            "checksum": request.checksum,
            "storage_ref": request.storage_ref,
            "storage_type": request.storage_type or "object_storage",
            "file_size": request.file_size
        }
        async with AsyncSessionLocal() as db:
            try:
                dataset, version = await dataset_registration_manager.register_dataset(db, payload)
                if HAS_PB2:
                    ver_msg = pb2.VersionMessage(
                        version_id=version.version_id,
                        dataset_id=version.dataset_id,
                        version_number=version.version_number,
                        checksum=version.checksum,
                        storage_ref=version.storage_ref,
                        status=version.status,
                        created_at=version.created_at.isoformat()
                    )
                    return pb2.DatasetDetailResponse(
                        dataset_id=dataset.dataset_id,
                        name=dataset.name,
                        description=dataset.description or "",
                        domain=dataset.domain,
                        source=dataset.source,
                        created_at=dataset.created_at.isoformat(),
                        updated_at=dataset.updated_at.isoformat(),
                        versions=[ver_msg]
                    )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))
                return pb2.DatasetDetailResponse() if HAS_PB2 else None

    async def ResolveIdentity(self, request, context):
        payload = {"name": request.name, "source": request.source, "domain": request.domain}
        async with AsyncSessionLocal() as db:
            is_existing, dataset, matched_by = await identity_resolution_manager.resolve_identity(db, payload)
            if HAS_PB2:
                return pb2.ResolveIdentityResponse(
                    is_existing=is_existing,
                    dataset_id=dataset.dataset_id if dataset else "",
                    matched_by=matched_by
                )

    async def CheckDuplicate(self, request, context):
        payload = {"checksum": request.checksum, "storage_ref": request.storage_ref}
        async with AsyncSessionLocal() as db:
            is_dup, dataset_id, version_id = await duplicate_detector.check_duplicate(db, payload)
            if HAS_PB2:
                return pb2.CheckDuplicateResponse(
                    is_duplicate=is_dup,
                    existing_dataset_id=dataset_id or "",
                    existing_version_id=version_id or "",
                    matched_checksum=request.checksum
                )


async def start_grpc_server():
    if not HAS_PB2:
        logger.info("Protobuf definitions not pre-compiled. Skipping gRPC server launch.")
        return None

    server = grpc.aio.server()
    pb2_grpc.add_DatasetCatalogServiceServicer_to_server(DatasetCatalogGrpcServicer(), server)
    listen_addr = f"[::]:{settings.GRPC_PORT}"
    server.add_insecure_port(listen_addr)
    await server.start()
    logger.info(f"gRPC Server listening on {listen_addr}")
    return server
