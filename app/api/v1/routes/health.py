import time

from fastapi import APIRouter

router = APIRouter(tags=["Health"])
_started = time.monotonic()


@router.get("/health", summary="Liveness check")
def health():
    return {"status": "ok", "uptimeSeconds": round(time.monotonic() - _started)}
