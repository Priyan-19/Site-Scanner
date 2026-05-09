"""
SiteScanner Core - WHOIS & DNS Scanner
Domain intelligence: registrar, age, expiry, DNS records.
"""
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Optional
from app.models import WhoisResult
from app.core.logging import get_logger

logger = get_logger("scanner.whois")


def _run_whois(domain: str) -> dict:
    """Sync WHOIS lookup. Run in thread pool."""
    try:
        import whois
        w = whois.whois(domain)
        return {
            "success": True,
            "registrar": getattr(w, "registrar", None),
            "creation_date": getattr(w, "creation_date", None),
            "expiration_date": getattr(w, "expiration_date", None),
            "name_servers": getattr(w, "name_servers", []),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _run_dns(domain: str) -> Dict[str, List[str]]:
    """Sync DNS record lookup. Run in thread pool."""
    records: Dict[str, List[str]] = {}
    try:
        import dns.resolver
        for rtype in ["A", "AAAA", "MX", "TXT", "NS", "CNAME"]:
            try:
                answers = dns.resolver.resolve(domain, rtype, lifetime=5)
                records[rtype] = [str(r) for r in answers]
            except Exception:
                pass
    except ImportError:
        logger.warning("dnspython not installed; skipping DNS resolution")
    return records


def _parse_date(dt) -> Optional[str]:
    """Normalize date from WHOIS (can be list or datetime)."""
    if isinstance(dt, list):
        dt = dt[0]
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d")
    if isinstance(dt, str):
        return dt[:10]
    return None


def _domain_age_days(creation) -> Optional[int]:
    if isinstance(creation, list):
        creation = creation[0]
    if isinstance(creation, datetime):
        if creation.tzinfo is None:
            creation = creation.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - creation).days
    return None


async def scan_whois(target: str) -> WhoisResult:
    """WHOIS lookup + DNS record fetch."""
    loop = asyncio.get_event_loop()

    # Run both in parallel via executor
    whois_task = loop.run_in_executor(None, _run_whois, target)
    dns_task = loop.run_in_executor(None, _run_dns, target)

    whois_data, dns_records = await asyncio.gather(whois_task, dns_task, return_exceptions=True)

    if isinstance(whois_data, Exception):
        whois_data = {"success": False, "error": str(whois_data)}
    if isinstance(dns_records, Exception):
        dns_records = {}

    if not whois_data.get("success"):
        logger.warning(f"WHOIS failed: {target} - {whois_data.get('error')}")
        return WhoisResult(
            domain=target,
            dns_records=dns_records if isinstance(dns_records, dict) else {},
            error=whois_data.get("error", "WHOIS lookup failed"),
        )

    creation = whois_data.get("creation_date")
    expiration = whois_data.get("expiration_date")

    # Name servers cleanup
    ns = whois_data.get("name_servers") or []
    if isinstance(ns, str):
        ns = [ns]
    ns = list(set(str(n).lower() for n in ns if n))

    logger.info(f"WHOIS done: {target} | age={_domain_age_days(creation)}d")

    return WhoisResult(
        domain=target,
        registrar=str(whois_data.get("registrar", "")) or None,
        creation_date=_parse_date(creation),
        expiration_date=_parse_date(expiration),
        domain_age_days=_domain_age_days(creation),
        name_servers=ns[:10],
        dns_records=dns_records if isinstance(dns_records, dict) else {},
    )
