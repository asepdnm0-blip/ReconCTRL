"""Synchronous database helpers for Celery workers (no asyncio event loop)."""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator, Optional

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker, selectinload

from app.config import settings
from app.models.scan import Scan, ScanModule, ScanStatus, ModuleStatus


def _sync_database_url(url: str) -> str:
    """Convert asyncpg URL to psycopg2 for sync worker sessions."""
    if "+asyncpg" in url:
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


_worker_engine = create_engine(
    _sync_database_url(settings.DATABASE_URL),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)
WorkerSessionLocal = sessionmaker(
    bind=_worker_engine,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@contextmanager
def worker_session() -> Generator[Session, None, None]:
    session = WorkerSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_scan(scan_id: str) -> Optional[Scan]:
    try:
        uid = uuid.UUID(scan_id)
    except ValueError:
        return None
    with worker_session() as db:
        result = db.execute(
            select(Scan)
            .options(selectinload(Scan.modules))
            .where(Scan.id == uid)
        )
        scan = result.scalars().first()
        if scan is not None:
            modules = list(scan.modules)
            for mod in modules:
                db.expunge(mod)
            db.expunge(scan)
        return scan


def set_scan_status(
    scan_id: str,
    status: ScanStatus,
    *,
    progress: Optional[int] = None,
    results_summary: Optional[dict[str, Any]] = None,
    error_message: Optional[str] = None,
) -> None:
    try:
        uid = uuid.UUID(scan_id)
    except ValueError:
        return

    with worker_session() as db:
        result = db.execute(select(Scan).where(Scan.id == uid))
        scan = result.scalars().first()
        if scan is None:
            return

        scan.status = status
        if progress is not None:
            scan.progress = progress
        if results_summary is not None:
            scan.results_summary = results_summary
        if error_message is not None:
            scan.error_message = error_message

        now = datetime.now(timezone.utc)
        if status == ScanStatus.RUNNING and scan.started_at is None:
            scan.started_at = now
        elif status in (ScanStatus.COMPLETED, ScanStatus.FAILED):
            scan.completed_at = now


def set_module_status(
    scan_id: str,
    module_name: str,
    status: ModuleStatus,
    *,
    progress: int = 0,
    result_data: Optional[dict[str, Any]] = None,
    error_message: Optional[str] = None,
) -> None:
    try:
        uid = uuid.UUID(scan_id)
    except ValueError:
        return

    with worker_session() as db:
        result = db.execute(
            select(ScanModule).where(
                ScanModule.scan_id == uid,
                ScanModule.module_name == module_name,
            )
        )
        module = result.scalars().first()
        if module is None:
            return

        module.status = status
        module.progress = progress
        if result_data is not None:
            module.result_data = result_data
        if error_message is not None:
            module.error_message = error_message

        now = datetime.now(timezone.utc)
        if status == ModuleStatus.RUNNING and module.started_at is None:
            module.started_at = now
        elif status in (ModuleStatus.COMPLETED, ModuleStatus.FAILED):
            module.completed_at = now
