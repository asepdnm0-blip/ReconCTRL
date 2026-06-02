from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def healthcheck():
    """Basic liveness probe."""
    return {"status": "ok", "service": "reconctrl-backend"}
