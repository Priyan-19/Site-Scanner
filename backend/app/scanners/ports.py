"""
SiteScanner Core - Port Scanner
Fast parallel TCP port scanning using ThreadPoolExecutor.
Defensive only. No exploit or banner grabbing beyond service ID.
"""
import socket
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List
from app.models import PortResult
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger("scanner.ports")
settings = get_settings()

# Port → (service name, risk, notes)
PORT_INFO: dict = {
    21:   ("FTP",         "HIGH",   "Unencrypted file transfer. Prefer SFTP/FTPS."),
    22:   ("SSH",         "MEDIUM", "Secure shell. Ensure key-based auth; disable password auth."),
    25:   ("SMTP",        "MEDIUM", "Mail relay. Verify SPF/DKIM/DMARC; restrict open relay."),
    53:   ("DNS",         "LOW",    "Domain resolution. Verify zone transfer restrictions."),
    80:   ("HTTP",        "LOW",    "Unencrypted web traffic. Redirect to HTTPS."),
    443:  ("HTTPS",       "INFO",   "Encrypted web traffic. Verify TLS version and cert."),
    3306: ("MySQL",       "CRITICAL","Database exposed publicly. Restrict to localhost."),
    5432: ("PostgreSQL",  "CRITICAL","Database exposed publicly. Restrict to localhost."),
    8080: ("HTTP-Alt",    "MEDIUM", "Alternate HTTP port. Ensure not dev/debug server."),
    8443: ("HTTPS-Alt",   "LOW",    "Alternate HTTPS port. Verify TLS configuration."),
}


def _check_port(host: str, port: int, timeout: float) -> PortResult:
    """Synchronous TCP connect check. Run in thread pool."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            open_ = True
    except (socket.timeout, ConnectionRefusedError, OSError):
        open_ = False

    info = PORT_INFO.get(port, ("Unknown", "LOW", "Unrecognized port."))
    service, risk, notes = info

    # Downgrade risk for closed ports
    if not open_:
        risk = "INFO"

    return PortResult(
        port=port,
        open=open_,
        service=service,
        risk=risk,
        notes=notes if open_ else "Port closed.",
    )


async def scan_ports(target: str) -> List[PortResult]:
    """Parallel port scan using thread pool, async-friendly."""
    loop = asyncio.get_event_loop()
    ports = settings.target_ports
    timeout = settings.port_scan_timeout

    logger.info(f"Port scan start: {target} → {ports}")

    with ThreadPoolExecutor(max_workers=min(len(ports), 20)) as pool:
        tasks = [
            loop.run_in_executor(pool, _check_port, target, port, timeout)
            for port in ports
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    port_results: List[PortResult] = []
    for r in results:
        if isinstance(r, PortResult):
            port_results.append(r)
        else:
            logger.warning(f"Port check error: {r}")

    open_count = sum(1 for p in port_results if p.open)
    logger.info(f"Port scan done: {target} → {open_count}/{len(ports)} open")
    return sorted(port_results, key=lambda x: x.port)
