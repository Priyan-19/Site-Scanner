"""
SiteScanner Core - Website Scanner
HTTP analysis: status, redirects, headers, timing.
"""
import time
import httpx
from typing import Optional
from app.models import WebsiteInfo
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger("scanner.website")
settings = get_settings()


async def scan_website(target: str) -> WebsiteInfo:
    """Analyze HTTP/HTTPS reachability, redirects, server info."""
    url = f"https://{target}"
    redirect_chain: list[str] = []
    is_https = False
    status_code = None
    final_url = None
    server = None
    content_type = None
    response_time_ms = None
    reachable = False

    start = time.monotonic()

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=settings.scan_timeout,
            verify=False,  # We inspect SSL separately
        ) as client:
            resp = await client.get(url)
            elapsed = (time.monotonic() - start) * 1000

            # Build redirect chain
            for r in resp.history:
                redirect_chain.append(str(r.url))
            redirect_chain.append(str(resp.url))

            status_code = resp.status_code
            final_url = str(resp.url)
            is_https = str(resp.url).startswith("https://")
            server = resp.headers.get("server")
            content_type = resp.headers.get("content-type")
            response_time_ms = round(elapsed, 2)
            reachable = True

            logger.info(f"Website OK: {target} → {status_code} ({response_time_ms}ms)")

    except httpx.ConnectError:
        # Try HTTP fallback
        try:
            url_http = f"http://{target}"
            async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
                resp = await client.get(url_http)
                elapsed = (time.monotonic() - start) * 1000
                for r in resp.history:
                    redirect_chain.append(str(r.url))
                redirect_chain.append(str(resp.url))
                status_code = resp.status_code
                final_url = str(resp.url)
                is_https = str(resp.url).startswith("https://")
                server = resp.headers.get("server")
                content_type = resp.headers.get("content-type")
                response_time_ms = round(elapsed, 2)
                reachable = True
                logger.info(f"Website OK (HTTP fallback): {target} → {status_code}")
        except Exception as e:
            logger.warning(f"Website unreachable: {target} - {e}")

    except Exception as e:
        logger.warning(f"Website scan error: {target} - {e}")

    return WebsiteInfo(
        url=f"https://{target}",
        status_code=status_code,
        https=is_https,
        redirect_chain=redirect_chain,
        final_url=final_url,
        server=server,
        content_type=content_type,
        response_time_ms=response_time_ms,
        reachable=reachable,
    )
