import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.constants import LifecycleState

if TYPE_CHECKING:
    from app.models.dataset_version import DatasetVersion


class ProcessingStatus(Base):
    __tablename__ = "processing_statuses"

    status_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("dataset_versions.version_id"), nullable=False, index=True
    )
    state: Mapped[str] = mapped_column(
        String(50), nullable=False, default=LifecycleState.RAW_REGISTERED.value
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    version: Mapped["DatasetVersion"] = relationship("DatasetVersion", back_populates="processing_statuses")
