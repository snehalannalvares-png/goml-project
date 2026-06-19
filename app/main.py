import logging
import logging.config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.middleware.logging import JsonAccessLogMiddleware
from app.routers import auth

settings = get_settings()

logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(message)s",
)

app = FastAPI(
    title="MXTZ Backend API",
    version="1.0.0",
    docs_url="/docs" if settings.environment == "dev" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to Flutter app origin in prod
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(JsonAccessLogMiddleware)

app.include_router(auth.router)


@app.get("/health", tags=["health"])
async def health():
    return JSONResponse({"status": "ok"})
