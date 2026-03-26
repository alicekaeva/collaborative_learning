from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import RedirectException
from app.api.v1.router import api_router
from app.web.router import web_router
from app.services.cache import close_redis

# Ensure upload directories exist before FastAPI mounts static files
_uploads_root = Path(settings.UPLOAD_DIR).parent
_uploads_root.mkdir(parents=True, exist_ok=True)
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="REST API платформы для совместного обучения",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

_allow_credentials = "*" not in settings.ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files statically at /uploads/materials/<filename>
app.mount("/uploads", StaticFiles(directory=str(_uploads_root)), name="uploads")

# Web UI (SSR) — must be before API router so "/" route is not shadowed
app.include_router(web_router)

# REST API
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.exception_handler(RedirectException)
async def redirect_exception_handler(request: Request, exc: RedirectException) -> RedirectResponse:
    return RedirectResponse(exc.url, status_code=303)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
