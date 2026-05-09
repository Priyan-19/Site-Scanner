"""
SiteScanner Core - Error Handling Middleware
Global exception handler. Structured JSON errors, no stack trace leaks.
"""
import time
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger

logger = get_logger("middleware")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.monotonic()
        try:
            response = await call_next(request)
            elapsed = (time.monotonic() - start) * 1000
            logger.debug(f"{request.method} {request.url.path} → {response.status_code} ({elapsed:.0f}ms)")
            return response
        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            logger.error(f"Unhandled error: {request.method} {request.url.path} - {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "detail": "An unexpected error occurred. Please try again.",
                    "path": str(request.url.path),
                }
            )


class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.monotonic()
        response = await call_next(request)
        elapsed = (time.monotonic() - start) * 1000
        response.headers["X-Response-Time"] = f"{elapsed:.2f}ms"
        return response
