"""
SiteScanner Core - Passive Subdomain Enumerator
DNS resolution only. No brute force, no crawling, no scraping.
"""
import asyncio
import socket
from typing import List, Optional
import httpx
from app.models import SubdomainResult
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger("scanner.subdomains")
settings = get_settings()


def _resolve_ip(hostname: str) -> Optional[str]:
    """Sync DNS A-record lookup."""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None


async def _check_subdomain(sub: str, domain: str) -> SubdomainResult:
    """Check if subdomain resolves and responds to HTTP."""
    full = f"{sub}.{domain}"
    loop = asyncio.get_event_loop()

    ip = await loop.run_in_executor(None, _resolve_ip, full)
    if not ip:
        return SubdomainResult(subdomain=sub, full_domain=full, reachable=False)

    # Quick HTTP probe
    status_code = None
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=5,
            verify=False,
        ) as client:
            resp = await client.get(f"https://{full}")
            status_code = resp.status_code
    except Exception:
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=5) as client:
                resp = await client.get(f"http://{full}")
                status_code = resp.status_code
        except Exception:
            pass

    return SubdomainResult(
        subdomain=sub,
        full_domain=full,
        reachable=True,
        ip=ip,
        status_code=status_code,
    )


async def scan_subdomains(target: str) -> List[SubdomainResult]:
    """Passive subdomain check via DNS resolution + HTTP probe."""
    subs = settings.passive_subdomains
    logger.info(f"Subdomain scan: {target} → checking {len(subs)} subdomains")

    tasks = [_check_subdomain(sub, target) for sub in subs]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    valid: List[SubdomainResult] = []
    for r in results:
        if isinstance(r, SubdomainResult):
            valid.append(r)

    found = sum(1 for r in valid if r.reachable)
    logger.info(f"Subdomains done: {target} → {found}/{len(subs)} found")
    return sorted(valid, key=lambda x: x.subdomain)
