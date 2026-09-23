import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.dataset_version import DatasetVersion


class StorageReference(Base):
    __tablename__ = "storage_references"

    storage_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("dataset_versions.version_id"), nullable=False, unique=True, index=True
    )
    uri: Mapped[str] = mapped_column(String(512), nullable=False)
    storage_type: Mapped[str] = mapped_column(String(50), nullable=False, default="object_storage")
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    version: Mapped["DatasetVersion"] = relationship("DatasetVersion", back_populates="storage_reference")
