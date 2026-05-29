"""REST + SSE routes consumed by the React dashboard."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
import httpx

from app.auth.clerk import create_access_token, require_user
from app.config import settings
from app.pipeline.catalog import load_catalog
from app.realtime.events import event_stream, subscribe
from app.storage.db import fetch_recent_events

router = APIRouter(prefix="/api", tags=["api"])


class LoginRequest(BaseModel):
    password: str


@router.post("/auth/login")
async def login(body: LoginRequest):
    if not settings.operator_password or body.password != settings.operator_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    return {"access_token": create_access_token(), "token_type": "bearer"}


@router.get("/quotes")
async def list_quotes(
    limit: int = Query(default=50, le=200),
    _user: dict = Depends(require_user),
):
    events = await fetch_recent_events(limit)
    return events


@router.get("/events/stream")
async def sse_stream(_user: dict = Depends(require_user)):
    """Server-Sent Events endpoint — pushes AgentEvent JSON to dashboard."""
    q = subscribe()
    return StreamingResponse(
        event_stream(q),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/catalog")
async def get_catalog(_user: dict = Depends(require_user)):
    import json
    from pathlib import Path
    path = Path(__file__).parent.parent.parent / "data" / "catalog.seed.json"
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/media/proxy")
async def proxy_media(url: str = Query(...)):
    """Fetch a Twilio media URL server-side (adding Basic Auth) and return the bytes.
    Restricted to twilio.com and api.twilio.com hostnames only."""
    from urllib.parse import urlparse
    host = urlparse(url).hostname or ""
    if not (host == "api.twilio.com" or host.endswith(".twilio.com")):
        raise HTTPException(status_code=400, detail="Only Twilio media URLs are proxied.")

    auth = None
    if settings.twilio_account_sid and settings.twilio_auth_token:
        auth = (settings.twilio_account_sid, settings.twilio_auth_token)

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, auth=auth)
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Media fetch failed: {exc}")

    media_type = resp.headers.get("content-type", "image/jpeg").split(";")[0]
    return Response(content=resp.content, media_type=media_type)


@router.post("/catalog/reload")
async def reload_catalog(_user: dict = Depends(require_user)):
    """Re-read catalog.seed.json without restarting the server."""
    load_catalog()
    import app.pipeline.catalog as cat
    return {"reloaded": len(cat._catalog), "skus": [s.id for s in cat._catalog]}
