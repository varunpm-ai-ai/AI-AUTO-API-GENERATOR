"""
File Type Detection Stage.
Detects true MIME and format using magic bytes inspection.
"""
from app.pipeline.stage import IPipelineStage
from app.core.context import PipelineContext
from app.extraction.detector import FileTypeDetector
from app.config.logger import get_logger

logger = get_logger(__name__)


class DetectionStage(IPipelineStage):
    """Stage 2: Identifies format and MIME type using magic signatures."""

    @property
    def name(self) -> str:
        return "file_type_detection"

    def execute(self, context: PipelineContext) -> None:
        if not context.local_raw_path or not context.local_raw_path.exists():
            raise FileNotFoundError("Local raw dataset file missing for detection.")

        mime_type, format_code = FileTypeDetector.detect(context.local_raw_path)
        context.detected_mime = mime_type
        context.detected_format = format_code

        logger.info(
            f"Detected dataset format: '{format_code}' (MIME: {mime_type}) for file {context.local_raw_path.name}"
        )
