"""Instagram DM via Meta Graph API webhook handler."""
import hashlib
import hmac
import json

import httpx
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Query, Request, status

from app.config import settings
from app.pipeline.orchestrator import run_pipeline

router = APIRouter(tags=["instagram"])

GRAPH_API = "https://graph.facebook.com/v21.0"


def _verify_meta_signature(body: bytes, signature: str) -> bool:
    if not signature.startswith("sha256="):
        return False
    expected = hmac.new(
        settings.meta_app_secret.encode(), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature[7:])


async def _reply(recipient_id: str, text: str) -> None:
    async with httpx.AsyncClient(timeout=15) as client:
        await client.post(
            f"{GRAPH_API}/me/messages",
            params={"access_token": settings.meta_page_access_token},
            json={
                "recipient": {"id": recipient_id},
                "message": {"text": text},
            },
        )


@router.get("/webhook/instagram")
async def ig_verify(
    hub_mode: str = Query(alias="hub.mode", default=""),
    hub_challenge: str = Query(alias="hub.challenge", default=""),
    hub_verify_token: str = Query(alias="hub.verify_token", default=""),
):
    """Meta webhook verification handshake."""
    if hub_mode == "subscribe" and hub_verify_token == settings.meta_verify_token:
        return int(hub_challenge)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed")


@router.post("/webhook/instagram")
async def ig_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(default=""),
):
    body = await request.body()

    if settings.meta_app_secret and not _verify_meta_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bad signature")

    payload = json.loads(body)

    for entry in payload.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender_id: str = messaging.get("sender", {}).get("id", "")
            message = messaging.get("message", {})
            attachments = message.get("attachments", [])

            for att in attachments:
                if att.get("type") == "image":
                    image_url: str = att["payload"].get("url", "")
                    if image_url and sender_id:
                        background_tasks.add_task(
                            run_pipeline,
                            image_url=image_url,
                            channel="instagram",
                            sender=sender_id,
                            reply_fn=_reply,
                        )

    return {"status": "ok"}
