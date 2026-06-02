import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String, Integer, DateTime, ForeignKey, Text, Enum as SAEnum, func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class ScanStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModuleStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    target: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    scan_type: Mapped[str] = mapped_column(String(50), nullable=False, default="full")
    status: Mapped[ScanStatus] = mapped_column(
        SAEnum(ScanStatus, name="scan_status", create_constraint=True),
        default=ScanStatus.QUEUED,
        index=True,
    )
    progress: Mapped[int] = mapped_column(Integer, default=0)
    results_summary: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # foreign keys
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # relationships
    owner: Mapped["User"] = relationship("User", back_populates="scans")
    modules: Mapped[list["ScanModule"]] = relationship(
        "ScanModule", back_populates="scan", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Scan {self.id} target={self.target} status={self.status}>"


class ScanModule(Base):
    __tablename__ = "scan_modules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False
    )
    module_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[ModuleStatus] = mapped_column(
        SAEnum(ModuleStatus, name="module_status", create_constraint=True),
        default=ModuleStatus.PENDING,
    )
    progress: Mapped[int] = mapped_column(Integer, default=0)
    result_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # relationships
    scan: Mapped["Scan"] = relationship("Scan", back_populates="modules")

    def __repr__(self) -> str:
        return f"<ScanModule {self.module_name} status={self.status}>"
