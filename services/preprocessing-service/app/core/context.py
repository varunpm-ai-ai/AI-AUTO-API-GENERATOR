"""
Pipeline Execution Context.
Encapsulates state, configuration, ephemeral artifacts, and telemetry across all processing stages.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from pathlib import Path
import time
import pandas as pd


@dataclass
class StageMetric:
    """Execution metrics for an individual pipeline stage."""
    stage_name: str
    duration_ms: float
    status: str = "SUCCESS"
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineContext:
    """
    Context object passed along the processing pipeline chain.
    Maintains ephemeral file paths, stage outputs, metadata, and telemetry.
    """
    job_id: str
    dataset_id: str
    correlation_id: str
    source_uri: str
    cleaning_config: Dict[str, Any] = field(default_factory=dict)
    
    # Filesystem / Scratch management
    scratch_dir: Optional[Path] = None
    local_raw_path: Optional[Path] = None
    local_processed_path: Optional[Path] = None
    extracted_files: List[Path] = field(default_factory=list)
    
    # Detection & Parsing artifacts
    detected_mime: Optional[str] = None
    detected_format: Optional[str] = None
    current_dataframe: Optional[pd.DataFrame] = None
    
    # Metadata & Results
    dataset_metadata: Dict[str, Any] = field(default_factory=dict)
    validation_report: Dict[str, Any] = field(default_factory=dict)
    output_s3_uri: Optional[str] = None
    
    # Telemetry and Execution state
    stage_metrics: List[StageMetric] = field(default_factory=list)
    is_cancelled: bool = False
    start_time: float = field(default_factory=time.time)

    def record_stage_metric(self, stage_name: str, duration_ms: float, status: str = "SUCCESS", details: Optional[Dict[str, Any]] = None):
        """Records telemetry for an executed stage."""
        self.stage_metrics.append(StageMetric(
            stage_name=stage_name,
            duration_ms=duration_ms,
            status=status,
            details=details or {}
        ))

    def get_total_duration_ms(self) -> float:
        """Returns the total elapsed runtime from start in milliseconds."""
        return (time.time() - self.start_time) * 1000.0
