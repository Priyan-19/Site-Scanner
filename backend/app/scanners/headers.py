"""
SiteScanner Core - Security Headers Scanner
Detect missing/misconfigured security headers with OWASP mapping.
"""
import httpx
from typing import List, Dict, Any
from app.models import HeaderAnalysis, Severity
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger("scanner.headers")
settings = get_settings()

# Header definitions: name → (severity, issue, remediation, owasp)
HEADER_CHECKS: Dict[str, tuple] = {
    "content-security-policy": (
        Severity.HIGH,
        "Missing Content-Security-Policy header. Allows XSS and injection attacks.",
        "Add CSP header: Content-Security-Policy: default-src 'self'; script-src 'self'",
        "A03:2021 - Injection / A05:2021 - Security Misconfiguration"
    ),
    "strict-transport-security": (
        Severity.HIGH,
        "Missing HSTS. Browser may downgrade to HTTP allowing MITM attacks.",
        "Add: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
        "A02:2021 - Cryptographic Failures"
    ),
    "x-frame-options": (
        Severity.MEDIUM,
        "Missing X-Frame-Options. Site vulnerable to clickjacking attacks.",
        "Add: X-Frame-Options: DENY or SAMEORIGIN",
        "A05:2021 - Security Misconfiguration"
    ),
    "x-content-type-options": (
        Severity.MEDIUM,
        "Missing X-Content-Type-Options. Allows MIME-type sniffing attacks.",
        "Add: X-Content-Type-Options: nosniff",
        "A05:2021 - Security Misconfiguration"
    ),
    "referrer-policy": (
        Severity.LOW,
        "Missing Referrer-Policy. Sensitive URL data may leak via Referer header.",
        "Add: Referrer-Policy: strict-origin-when-cross-origin",
        "A05:2021 - Security Misconfiguration"
    ),
    "permissions-policy": (
        Severity.LOW,
        "Missing Permissions-Policy. Browser features not restricted.",
        "Add: Permissions-Policy: geolocation=(), microphone=(), camera=()",
        "A05:2021 - Security Misconfiguration"
    ),
    "x-xss-protection": (
        Severity.LOW,
        "Missing X-XSS-Protection (legacy browsers).",
        "Add: X-XSS-Protection: 1; mode=block (for older browser support)",
        "A03:2021 - Injection"
    ),
}

# Headers that should NOT be present (information leakage)
LEAKY_HEADERS: List[str] = ["server", "x-powered-by", "x-aspnet-version", "x-aspnetmvc-version"]


async def scan_headers(target: str) -> List[HeaderAnalysis]:
    """Fetch response headers and analyze security posture."""
    results: List[HeaderAnalysis] = []
    raw_headers: Dict[str, str] = {}

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=15,
            verify=False,
        ) as client:
            resp = await client.get(f"https://{target}")
            raw_headers = dict(resp.headers)
    except Exception:
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
                resp = await client.get(f"http://{target}")
                raw_headers = dict(resp.headers)
        except Exception as e:
            logger.warning(f"Header scan failed: {target} - {e}")
            return results

    lower_headers = {k.lower(): v for k, v in raw_headers.items()}

    # Check required security headers
    for header_name, (severity, issue, remediation, owasp) in HEADER_CHECKS.items():
        present = header_name in lower_headers
        value = lower_headers.get(header_name)

        results.append(HeaderAnalysis(
            header=header_name,
            present=present,
            value=value,
            severity=severity if not present else Severity.INFO,
            issue=issue if not present else "Header present",
            remediation=remediation if not present else "No action needed",
            owasp=owasp,
        ))

    # Check leaky headers
    for lh in LEAKY_HEADERS:
        if lh in lower_headers:
            results.append(HeaderAnalysis(
                header=lh,
                present=True,
                value=lower_headers[lh],
                severity=Severity.LOW,
                issue=f"Information leakage: '{lh}' header reveals server details.",
                remediation=f"Remove or mask the '{lh}' header in server configuration.",
                owasp="A05:2021 - Security Misconfiguration",
            ))

    # Cookie security check
    set_cookie = lower_headers.get("set-cookie", "")
    if set_cookie:
        cookie_issues = []
        if "httponly" not in set_cookie.lower():
            cookie_issues.append("Missing HttpOnly flag")
        if "secure" not in set_cookie.lower():
            cookie_issues.append("Missing Secure flag")
        if "samesite" not in set_cookie.lower():
            cookie_issues.append("Missing SameSite attribute")

        if cookie_issues:
            results.append(HeaderAnalysis(
                header="set-cookie",
                present=True,
                value=set_cookie[:100],
                severity=Severity.MEDIUM,
                issue=f"Insecure cookie attributes: {', '.join(cookie_issues)}",
                remediation="Set cookies with: Secure; HttpOnly; SameSite=Strict",
                owasp="A02:2021 - Cryptographic Failures / A05:2021 - Security Misconfiguration",
            ))

    logger.info(f"Headers scanned: {target} → {len(results)} checks")
    return results
