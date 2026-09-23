from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.dataset_metadata import DatasetMetadata
from app.models.dataset_version import DatasetVersion
from app.logger import logger


class MetadataExtractor:
    """Extracts file-level and contextual metadata from file info."""
    @staticmethod
    def extract_metadata(payload: Dict[str, Any]) -> Dict[str, Any]:
        extracted = {}

        # Default system fields
        if "file_size" in payload:
            extracted["file_size_bytes"] = str(payload["file_size"])
        if "storage_type" in payload:
            extracted["storage_type"] = str(payload["storage_type"])

        # Storage extension format extraction
        storage_ref = payload.get("storage_ref", "")
        if "." in storage_ref:
            ext = storage_ref.split(".")[-1].split("?")[0].lower()
            extracted["file_extension"] = ext

        # Extract extra metadata dictionary if passed
        extra_meta = payload.get("metadata", {})
        if isinstance(extra_meta, dict):
            for k, v in extra_meta.items():
                extracted[str(k)] = str(v)

        return extracted


class MetadataManager:
    def __init__(self):
        self.extractor = MetadataExtractor()

    async def save_metadata(
        self,
        db: AsyncSession,
        version: DatasetVersion,
        payload: Dict[str, Any],
        source: str = "system"
    ) -> List[DatasetMetadata]:
        extracted_dict = self.extractor.extract_metadata(payload)
        saved_entries = []

        for key, value in extracted_dict.items():
            # Check if key already exists for this version
            query = select(DatasetMetadata).where(
                DatasetMetadata.version_id == version.version_id,
                DatasetMetadata.key == key
            )
            res = await db.execute(query)
            meta = res.scalar_one_or_none()

            if meta:
                meta.value = str(value)
                meta.source = source
            else:
                meta = DatasetMetadata(
                    version_id=version.version_id,
                    key=key,
                    value=str(value),
                    source=source
                )
                db.add(meta)

            saved_entries.append(meta)

        await db.flush()
        logger.info(f"Saved {len(saved_entries)} metadata entries for version '{version.version_id}'.")
        return saved_entries


metadata_manager = MetadataManager()
