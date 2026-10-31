"""
Archive Extraction Stage.
Safely extracts compressed archives into ephemeral scratch storage.
"""
from app.pipeline.stage import IPipelineStage
from app.core.context import PipelineContext
from app.extraction.extractor import ArchiveExtractor
from app.extraction.detector import FileTypeDetector
from app.config.logger import get_logger

logger = get_logger(__name__)


class ExtractionStage(IPipelineStage):
    """Stage 3: Extracts archives (ZIP/TAR/GZ) if applicable, updating local_raw_path."""

    @property
    def name(self) -> str:
        return "archive_extraction"

    def execute(self, context: PipelineContext) -> None:
        if not context.detected_format:
            return

        if ArchiveExtractor.is_archive(context.detected_format):
            extract_dir = context.scratch_dir / "extracted"
            extracted_files = ArchiveExtractor.extract(context.local_raw_path, extract_dir)
            context.extracted_files = extracted_files

            if not extracted_files:
                raise ValueError(f"Archive {context.local_raw_path.name} contains no usable files.")

            # Pick the primary data file (first non-hidden data file)
            primary_file = extracted_files[0]
            for f in extracted_files:
                if f.suffix.lower() in [".csv", ".tsv", ".json", ".parquet", ".xlsx"]:
                    primary_file = f
                    break

            context.local_raw_path = primary_file
            # Re-detect the inner file format
            mime_type, format_code = FileTypeDetector.detect(primary_file)
            context.detected_mime = mime_type
            context.detected_format = format_code
            logger.info(f"Archive extracted. Selected primary file: {primary_file.name} (Format: {format_code})")
