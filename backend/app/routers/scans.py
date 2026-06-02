import json
import uuid
from typing import Optional

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.scan import (
    ScanCreate,
    ScanDetailResponse,
    ScanListResponse,
    ScanResponse,
)
from app.services import auth_service, scan_service
from app.worker.celery_app import celery_app as celery

router = APIRouter(prefix="/scans", tags=["scans"])
security_scheme = HTTPBearer()


async def _resolve_user_from_token(token: str, db: AsyncSession) -> User:
    payload = auth_service.decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )
    user = await auth_service.get_user_by_id(db, payload["sub"])
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    return await _resolve_user_from_token(credentials.credentials, db)


@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    body: ScanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """Create a new scan and enqueue it to Celery."""
    scan = await scan_service.create_scan(
        db,
        target=body.target,
        scan_type=body.scan_type,
        modules=body.modules,
        owner_id=current_user.id,
    )
    celery.send_task(
        "worker.tasks.scan_task",
        args=[str(scan.id), body.target, body.modules],
    )
    return scan


@router.get("/", response_model=ScanListResponse)
async def list_scans(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """List scans for the authenticated user."""
    scans, total = await scan_service.list_scans(
        db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return ScanListResponse(items=scans, total=total)


@router.get("/{scan_id}", response_model=ScanDetailResponse)
async def get_scan(
    scan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """Get scan details including module results."""
    scan = await scan_service.get_scan_by_id(db, scan_id)
    if scan is None or scan.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return scan


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """Delete a scan owned by the authenticated user."""
    deleted = await scan_service.delete_scan(db, scan_id, owner_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")


@router.get("/{scan_id}/stream")
async def stream_scan_events(
    scan_id: uuid.UUID,
    token: str = Query(..., description="JWT access token (required for EventSource)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Server-Sent Events stream for real-time scan progress.

    Auth via query param `token` because browser EventSource cannot set headers.
    Subscribes to Redis channel `scan:{scan_id}:events` until `scan_complete`.
    """
    user = await _resolve_user_from_token(token, db)

    scan = await scan_service.get_scan_by_id(db, scan_id)
    if scan is None or scan.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")

    channel_name = f"scan:{scan_id}:events"

    async def event_generator():
        redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel_name)

        try:
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue

                try:
                    data = json.loads(message["data"])
                except (json.JSONDecodeError, TypeError):
                    data = {"raw": message["data"]}

                event_type = data.get("event", "message")

                yield {
                    "event": event_type,
                    "data": json.dumps(data),
                }

                if event_type == "scan_complete":
                    break
        finally:
            await pubsub.unsubscribe(channel_name)
            await pubsub.close()
            await redis_client.aclose()

    return EventSourceResponse(event_generator())
