"""
SiteScanner Core - Scan Orchestrator
Coordinates all scanners, updates WebSocket, stores results.
"""
import asyncio
import uuid
import time
from datetime import datetime
from app.models import ScanRequest, ScanResult, ScanStatus, WebsiteInfo
from app.scanners.website import scan_website
from app.scanners.headers import scan_headers
from app.scanners.ports import scan_ports
from app.scanners.ssl_scanner import scan_ssl
from app.scanners.whois_scanner import scan_whois
from app.scanners.subdomains import scan_subdomains
from app.services.risk_engine import compute_risk
from app.core.store import scan_store
from app.websocket.manager import ws_manager
from app.core.logging import get_logger

logger = get_logger("service.scan")


async def _update(scan_id: str, result: ScanResult, stage: str, progress: int, detail: str = "") -> None:
    """Persist progress + broadcast to WebSocket clients."""
    result.progress = progress
    result.current_stage = stage
    await scan_store.save(result)
    await ws_manager.send_progress(scan_id, stage, progress, detail)
    logger.info(f"[{scan_id[:8]}] {stage} ({progress}%) {detail}")


async def run_scan(request: ScanRequest) -> str:
    """Launch full scan pipeline. Returns scan_id immediately."""
    scan_id = str(uuid.uuid4())
    target = request.target

    result = ScanResult(
        scan_id=scan_id,
        target=target,
        status=ScanStatus.RUNNING,
        timestamp=datetime.utcnow(),
    )
    await scan_store.save(result)
    logger.info(f"Scan started: {scan_id[:8]} → {target}")

    # Fire-and-forget async
    asyncio.create_task(_execute_scan(scan_id, target, request, result))
    return scan_id


async def _execute_scan(
    scan_id: str,
    target: str,
    request: ScanRequest,
    result: ScanResult,
) -> None:
    start = time.monotonic()

    try:
        # ── Stage 1: Website ─────────────────────────────────────────────────
        await _update(scan_id, result, "checking_http", 10, f"Probing {target}")
        result.website = await scan_website(target)

        # ── Stage 2: Headers ─────────────────────────────────────────────────
        await _update(scan_id, result, "headers_analysis", 25, "Analyzing response headers")
        result.headers = await scan_headers(target)

        # ── Stage 3: SSL ─────────────────────────────────────────────────────
        if request.include_ssl:
            await _update(scan_id, result, "ssl_analysis", 40, "Inspecting certificate")
            result.ssl = await scan_ssl(target)

        # ── Stage 4: WHOIS ───────────────────────────────────────────────────
        if request.include_whois:
            await _update(scan_id, result, "whois_lookup", 55, "Fetching domain records")
            result.whois = await scan_whois(target)

        # ── Stage 5: Subdomains ──────────────────────────────────────────────
        if request.include_subdomains:
            await _update(scan_id, result, "subdomain_discovery", 70, "Passive subdomain detection")
            result.subdomains = await scan_subdomains(target)

        # ── Stage 6: Ports ───────────────────────────────────────────────────
        if request.include_ports:
            await _update(scan_id, result, "port_scanning", 82, "Parallel port analysis")
            result.ports = await scan_ports(target)

        # ── Stage 7: Risk Engine ─────────────────────────────────────────────
        await _update(scan_id, result, "finalizing", 92, "Computing security score")
        score, risk, issues, recs = compute_risk(result)
        result.security_score = score
        result.risk_level = risk
        result.issues = issues
        result.recommendations = recs

        elapsed = time.monotonic() - start
        result.scan_duration = f"{elapsed:.2f}s"
        result.status = ScanStatus.COMPLETED
        # ── Stage 8: Completed ───────────────────────────────────────────────
        await _update(scan_id, result, "completed", 100, "Scan finished successfully")
        
        await ws_manager.send_complete(scan_id, score, risk.value)
        logger.info(
            f"Scan complete: {scan_id[:8]} | score={score} risk={risk} "
            f"issues={len(issues)} duration={result.scan_duration}"
        )

    except Exception as e:
        result.status = ScanStatus.FAILED
        result.error = str(e)
        result.progress = 0
        elapsed = time.monotonic() - start
        result.scan_duration = f"{elapsed:.2f}s"
        await scan_store.save(result)
        await ws_manager.send_error(scan_id, str(e))
        logger.error(f"Scan failed: {scan_id[:8]} - {e}", exc_info=True)
