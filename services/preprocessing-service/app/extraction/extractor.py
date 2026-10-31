"""
Archive Decompression & Extraction Engine.
Provides secure extraction for ZIP, TAR, GZ archives with decompression ratio limits and path-traversal protection.
"""
from pathlib import Path
from typing import List
import zipfile
import tarfile
import gzip
import shutil
import os
from app.core.exceptions import ExtractionSecurityError, PreprocessingBaseException
from app.config.settings import settings
from app.config.logger import get_logger

logger = get_logger(__name__)


class ArchiveExtractor:
    """Safely extracts archives into a scoped temporary scratch workspace."""

    @classmethod
    def is_archive(cls, file_format: str) -> bool:
        return file_format in ["zip", "tar", "gzip", "gz"]

    @classmethod
    def extract(cls, archive_path: Path, destination_dir: Path) -> List[Path]:
        """
        Extracts an archive into destination_dir while strictly enforcing:
        1. Path traversal prevention (cannot write outside destination_dir).
        2. Decompression ratio limit (Zip Bomb protection).
        3. Max uncompressed size cap.
        Returns a list of extracted file paths.
        """
        ext = archive_path.suffix.lower()
        compressed_size = archive_path.stat().st_size
        max_allowed_uncompressed = compressed_size * settings.MAX_DECOMPRESSED_RATIO
        max_allowed_uncompressed = min(max_allowed_uncompressed, settings.MAX_FILE_SIZE_BYTES)

        destination_dir.mkdir(parents=True, exist_ok=True)
        canonical_dest = destination_dir.resolve()
        extracted_files: List[Path] = []
        total_extracted_bytes = 0

        # Handle ZIP Archives
        if ext == ".zip" or zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path, "r") as zf:
                for member in zf.infolist():
                    # Calculate uncompressed size
                    total_extracted_bytes += member.file_size
                    if total_extracted_bytes > max_allowed_uncompressed:
                        raise ExtractionSecurityError(
                            f"Archive exceeds maximum safe decompression ratio or size limit ({total_extracted_bytes} bytes)"
                        )

                    # Validate path traversal
                    target_path = (destination_dir / member.filename).resolve()
                    if not str(target_path).startswith(str(canonical_dest)):
                        raise ExtractionSecurityError(f"Path traversal detected in archive entry: {member.filename}")

                    if not member.is_dir():
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(member) as source, open(target_path, "wb") as target:
                            shutil.copyfileobj(source, target)
                        extracted_files.append(target_path)

            logger.info(f"Safely extracted {len(extracted_files)} files from ZIP: {archive_path.name}")
            return extracted_files

        # Handle TAR / TAR.GZ Archives
        if ext in [".tar", ".gz", ".tgz"] or tarfile.is_tarfile(archive_path):
            with tarfile.open(archive_path, "r:*") as tf:
                for member in tf.getmembers():
                    total_extracted_bytes += member.size
                    if total_extracted_bytes > max_allowed_uncompressed:
                        raise ExtractionSecurityError(
                            f"TAR archive exceeds safe decompression limit ({total_extracted_bytes} bytes)"
                        )

                    target_path = (destination_dir / member.name).resolve()
                    if not str(target_path).startswith(str(canonical_dest)):
                        raise ExtractionSecurityError(f"Path traversal detected in TAR entry: {member.name}")

                    if member.isfile():
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        extracted_file = tf.extractfile(member)
                        if extracted_file:
                            with open(target_path, "wb") as target:
                                shutil.copyfileobj(extracted_file, target)
                            extracted_files.append(target_path)

            logger.info(f"Safely extracted {len(extracted_files)} files from TAR: {archive_path.name}")
            return extracted_files

        # Handle standalone .GZ file (single compressed stream)
        if ext == ".gz":
            out_filename = archive_path.stem  # strips .gz
            target_path = destination_dir / out_filename
            with gzip.open(archive_path, "rb") as source, open(target_path, "wb") as target:
                shutil.copyfileobj(source, target)
            extracted_files.append(target_path)
            return extracted_files

        raise PreprocessingBaseException(f"Unsupported archive format: {archive_path.name}")
