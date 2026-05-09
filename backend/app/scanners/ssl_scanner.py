"""
SiteScanner Core - SSL/TLS Inspector
Certificate validity, expiry, issuer, TLS version analysis.
"""
import ssl
import socket
from datetime import datetime, timezone
from typing import Optional
from app.models import SSLResult
from app.core.logging import get_logger

logger = get_logger("scanner.ssl")


def _get_cert_info(hostname: str, port: int = 443, timeout: float = 10) -> dict:
    """Low-level SSL cert extraction. Sync; called via executor."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # We inspect manually

    info = {
        "connected": False,
        "cert": None,
        "tls_version": None,
        "error": None,
    }

    try:
        with socket.create_connection((hostname, port), timeout=timeout) as raw:
            with ctx.wrap_socket(raw, server_hostname=hostname) as ssock:
                info["connected"] = True
                info["cert"] = ssock.getpeercert()
                info["tls_version"] = ssock.version()
    except ssl.SSLError as e:
        info["error"] = f"SSL error: {e.reason}"
    except socket.timeout:
        info["error"] = "Connection timed out"
    except ConnectionRefusedError:
        info["error"] = "Port 443 not open"
    except Exception as e:
        info["error"] = str(e)

    return info


async def scan_ssl(target: str) -> SSLResult:
    """Inspect SSL certificate and TLS configuration."""
    import asyncio
    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(None, _get_cert_info, target)

    if not info["connected"]:
        return SSLResult(
            has_ssl=False,
            valid=False,
            issues=[info.get("error", "Could not connect to SSL endpoint")],
        )

    cert = info.get("cert") or {}
    tls_version = info.get("tls_version")
    issues = []

    # Parse expiry
    expires_str = None
    days_remaining = None
    expired = False

    not_after = cert.get("notAfter")
    if not_after:
        try:
            exp_dt = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
            exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            days_remaining = (exp_dt - now).days
            expired = days_remaining < 0
            expires_str = exp_dt.strftime("%Y-%m-%d")

            if expired:
                issues.append("Certificate has EXPIRED")
            elif days_remaining < 30:
                issues.append(f"Certificate expires in {days_remaining} days — renew soon")
        except Exception:
            pass

    # Parse issuer
    issuer_raw = cert.get("issuer", ())
    issuer = _parse_cert_field(issuer_raw)

    # Parse subject
    subject_raw = cert.get("subject", ())
    subject = _parse_cert_field(subject_raw)

    # Self-signed check
    self_signed = issuer == subject if issuer and subject else False
    if self_signed:
        issues.append("Self-signed certificate detected")

    # TLS version check
    weak_tls = ["TLSv1", "TLSv1.1", "SSLv2", "SSLv3"]
    if tls_version in weak_tls:
        issues.append(f"Weak TLS version in use: {tls_version}")

    # Validity
    valid = not expired and not self_signed and len(issues) == 0

    logger.info(f"SSL scanned: {target} → valid={valid} expires={expires_str} tls={tls_version}")

    return SSLResult(
        has_ssl=True,
        valid=valid,
        issuer=issuer,
        subject=subject,
        expires=expires_str,
        days_remaining=days_remaining,
        tls_version=tls_version,
        self_signed=self_signed,
        expired=expired,
        issues=issues,
    )


def _parse_cert_field(field: tuple) -> Optional[str]:
    """Extract CN from cert issuer/subject tuples."""
    try:
        for item in field:
            for k, v in item:
                if k == "commonName":
                    return v
        # Fallback: first value
        if field:
            return str(field[0])
    except Exception:
        pass
    return None
