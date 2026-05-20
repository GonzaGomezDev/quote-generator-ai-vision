from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.storage.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Quote Generator AI Vision", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers (imported after app creation to avoid circular imports) ─────────
from app.channels.whatsapp_twilio import router as wa_router        # noqa: E402
from app.channels.instagram_meta import router as ig_router         # noqa: E402
from app.web.routes import router as web_router                     # noqa: E402

app.include_router(wa_router)
app.include_router(ig_router)
app.include_router(web_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
