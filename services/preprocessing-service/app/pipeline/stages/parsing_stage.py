"""
Parsing Stage.
Uses DatasetAdapterFactory to instantiate the appropriate adapter and read raw dataset records.
"""
from app.pipeline.stage import IPipelineStage
from app.core.context import PipelineContext
from app.factories.adapter_factory import DatasetAdapterFactory
from app.config.logger import get_logger

logger = get_logger(__name__)


class ParsingStage(IPipelineStage):
    """Stage 4: Parses heterogeneous dataset content into tabular structure."""

    @property
    def name(self) -> str:
        return "data_parsing"

    def execute(self, context: PipelineContext) -> None:
        adapter = DatasetAdapterFactory.get_adapter(
            context.local_raw_path,
            context.detected_format or "csv"
        )
        # Parse DataFrame (with chunked reading or read_all depending on memory limits)
        df = adapter.read_all()
        if df.empty:
            logger.warning(f"Dataset {context.local_raw_path.name} parsed into an empty DataFrame")

        context.current_dataframe = df
        logger.info(f"Parsed {len(df)} rows and {len(df.columns)} columns using {adapter.__class__.__name__}")
