"""
SiteScanner Core - Main Application
FastAPI app factory with middleware, routes, CORS, rate limiting.
"""
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.middleware.error_handler import ErrorHandlerMiddleware, RequestTimingMiddleware
from app.routes.scan_routes import router
from app.routes.ws_routes import ws_router

# ── Logging setup (must be first) ─────────────────────────────────────────────
setup_logging()
logger = get_logger("main")
settings = get_settings()


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"")
    logger.info(f"  ███████╗██╗████████╗███████╗███████╗ ██████╗ █████╗ ███╗  ██╗███╗  ██╗███████╗██████╗ ")
    logger.info(f"  ██╔════╝██║╚══██╔══╝██╔════╝██╔════╝██╔════╝██╔══██╗████╗ ██║████╗ ██║██╔════╝██╔══██╗")
    logger.info(f"  ███████╗██║   ██║   █████╗  ███████╗██║     ███████║██╔██╗██║██╔██╗██║█████╗  ██████╔╝")
    logger.info(f"  ╚════██║██║   ██║   ██╔══╝  ╚════██║██║     ██╔══██║██║╚████║██║╚████║██╔══╝  ██╔══██╗")
    logger.info(f"  ███████║██║   ██║   ███████╗███████║╚██████╗██║  ██║██║ ╚███║██║ ╚███║███████╗██║  ██║")
    logger.info(f"  ╚══════╝╚═╝   ╚═╝   ╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚══╝╚═╝  ╚══╝╚══════╝╚═╝  ╚═╝")
    logger.info(f"")
    logger.info(f"  {settings.app_name} v{settings.app_version}")
    logger.info(f"  Defensive Cybersecurity Scanning Engine")
    logger.info(f"  ─────────────────────────────────────────")
    logger.info(f"  Host     : {settings.host}:{settings.port}")
    logger.info(f"  Debug    : {settings.debug}")
    logger.info(f"  Docs     : http://localhost:{settings.port}/docs")
    logger.info(f"  ReDoc    : http://localhost:{settings.port}/redoc")
    logger.info(f"  [!] Ethical use only. Defensive scanning.")
    logger.info(f"")
    yield
    logger.info("SiteScanner Core shutting down...")


# ── App factory ───────────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "**SiteScanner Core** — Defensive cybersecurity scanning engine. "
            "Ethical, audit-oriented web vulnerability analysis API.\n\n"
            "> ⚠️ **Ethical use only.** Only scan domains you own or have explicit permission to test."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────────────────────
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # ── Routes ────────────────────────────────────────────────────────────────
    app.include_router(router, prefix="/api/v1")
    app.include_router(ws_router, prefix="/api/v1")  # WebSocket under /api/v1 to match frontend

    # ── Convenience redirects ─────────────────────────────────────────────────
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/api/v1/health",
            "scan": "POST /api/v1/scan",
        }

    return app


app = create_app()
