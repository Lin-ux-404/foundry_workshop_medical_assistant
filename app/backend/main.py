"""FastAPI application for the Agentic Medical Operations Assistant (starter).

Run from the `app/backend/` folder:
    uvicorn main:app --reload
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from clients import create_credential, create_foundry_client
from routers import chat, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # One credential + client for the whole app lifetime.
    credential = create_credential()
    client = create_foundry_client(credential)
    app.state.foundry_client = client
    app.state.credential = credential
    try:
        yield
    finally:
        for closable in (client, credential):
            close = getattr(closable, "close", None)
            if close is not None:
                try:
                    await close()
                except Exception:  # noqa: BLE001 - best-effort shutdown
                    pass


app = FastAPI(
    title="Agentic Medical Operations Assistant API",
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
