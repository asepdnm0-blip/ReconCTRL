import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.scan import Scan, ScanModule, ScanStatus, ModuleStatus


async def create_scan(
    db: AsyncSession,
    target: str,
    scan_type: str,
    modules: List[str],
    owner_id: uuid.UUID,
) -> Scan:
    """Create a Scan record with its ScanModule children."""
    scan = Scan(
        target=target,
        scan_type=scan_type,
        status=ScanStatus.QUEUED,
        owner_id=owner_id,
    )
    db.add(scan)
    await db.flush()

    for mod_name in modules:
        module = ScanModule(
            scan_id=scan.id,
            module_name=mod_name,
            status=ModuleStatus.PENDING,
        )
        db.add(module)

    await db.flush()
    await db.refresh(scan)
    return scan


async def get_scan_by_id(
    db: AsyncSession, scan_id: uuid.UUID
) -> Optional[Scan]:
    """Fetch a scan with its modules eagerly loaded."""
    query = (
        select(Scan)
        .options(selectinload(Scan.modules))
        .where(Scan.id == scan_id)
    )
    result = await db.execute(query)
    return result.scalars().first()


async def list_scans(
    db: AsyncSession,
    owner_id: uuid.UUID,
    skip: int = 0,
    limit: int = 20,
) -> tuple[List[Scan], int]:
    """List scans for a user with pagination."""
    count_query = select(func.count(Scan.id)).where(Scan.owner_id == owner_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    query = (
        select(Scan)
        .where(Scan.owner_id == owner_id)
        .order_by(Scan.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    scans = list(result.scalars().all())
    return scans, total


async def update_scan_status(
    db: AsyncSession,
    scan_id: uuid.UUID,
    status: ScanStatus,
    error_message: Optional[str] = None,
) -> Optional[Scan]:
    """Update scan status and timestamps."""
    scan = await get_scan_by_id(db, scan_id)
    if scan is None:
        return None

    scan.status = status
    if status == ScanStatus.RUNNING and scan.started_at is None:
        scan.started_at = datetime.now(timezone.utc)
    elif status in (ScanStatus.COMPLETED, ScanStatus.FAILED, ScanStatus.CANCELLED):
        scan.completed_at = datetime.now(timezone.utc)
    if error_message:
        scan.error_message = error_message

    await db.flush()
    await db.refresh(scan)
    return scan


async def delete_scan(
    db: AsyncSession,
    scan_id: uuid.UUID,
    owner_id: uuid.UUID,
) -> bool:
    """Delete a scan if it belongs to the given owner."""
    scan = await get_scan_by_id(db, scan_id)
    if scan is None or scan.owner_id != owner_id:
        return False
    await db.delete(scan)
    await db.flush()
    return True
