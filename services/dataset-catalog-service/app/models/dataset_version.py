import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.constants import LifecycleState

if TYPE_CHECKING:
    from app.models.dataset import Dataset
    from app.models.dataset_metadata import DatasetMetadata
    from app.models.storage_reference import StorageReference
    from app.models.processing_status import ProcessingStatus


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    version_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    dataset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("datasets.dataset_id"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    storage_ref: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=LifecycleState.RAW_REGISTERED.value
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="versions")
    metadata_entries: Mapped[List["DatasetMetadata"]] = relationship(
        "DatasetMetadata", back_populates="version", cascade="all, delete-orphan"
    )
    storage_reference: Mapped[Optional["StorageReference"]] = relationship(
        "StorageReference", back_populates="version", uselist=False, cascade="all, delete-orphan"
    )
    processing_statuses: Mapped[List["ProcessingStatus"]] = relationship(
        "ProcessingStatus", back_populates="version", cascade="all, delete-orphan"
    )
