"""
SiteScanner Core - API Routes
Clean REST endpoints with input validation and error handling.
"""
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
import io
from app.models import ScanRequest, ScanResult, ScanSummary, HealthResponse
from app.services.scan_service import run_scan
from app.core.store import scan_store
from app.reports.pdf_generator import generate_pdf
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger("routes")
settings = get_settings()
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        app_name=settings.app_name,
    )


@router.post("/scan", tags=["Scanning"])
async def start_scan(request: ScanRequest):
    """
    Start a new security scan.
    Returns scan_id immediately; use GET /scan/{id} to poll results.
    """
    logger.info(f"POST /scan → target={request.target}")
    scan_id = await run_scan(request)
    return {
        "scan_id": scan_id,
        "target": request.target,
        "status": "running",
        "message": f"Scan started. Poll GET /scan/{scan_id} for results.",
        "websocket": f"/api/v1/ws/scan/{scan_id}",
    }


@router.get("/scan/{scan_id}", response_model=ScanResult, tags=["Scanning"])
async def get_scan(scan_id: str):
    """Get full scan result by ID."""
    result = await scan_store.get(scan_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Scan '{scan_id}' not found")
    return result


@router.get("/history", response_model=list[ScanSummary], tags=["History"])
async def scan_history():
    """Return in-memory scan history (most recent first)."""
    return await scan_store.history()


@router.get("/report/{scan_id}", tags=["Reports"])
async def download_report(scan_id: str, format: str = "pdf"):
    """
    Download scan report.
    - format=pdf → PDF file
    - format=json → JSON file
    """
    result = await scan_store.get(scan_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Scan '{scan_id}' not found")

    if result.status.value != "completed":
        raise HTTPException(status_code=400, detail="Scan not yet completed")

    if format == "json":
        import json
        content = result.model_dump_json(indent=2)
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="scan_{scan_id[:8]}.json"'}
        )

    # PDF
    try:
        pdf_bytes = generate_pdf(result)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="scan_{scan_id[:8]}.pdf"'}
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"PDF generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")
