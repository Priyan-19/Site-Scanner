"""
SiteScanner Core - Risk Scoring Engine
Weighted 0-100 security score + issue aggregation.
"""
from typing import List, Tuple
from app.models import (
    ScanResult, RiskLevel, SecurityIssue, Severity,
    HeaderAnalysis, PortResult, SSLResult, WebsiteInfo
)
from app.core.logging import get_logger

logger = get_logger("engine.risk")

# Severity weights (score deductions)
SEVERITY_WEIGHTS = {
    Severity.CRITICAL: 25,
    Severity.HIGH:     15,
    Severity.MEDIUM:   8,
    Severity.LOW:      3,
    Severity.INFO:     0,
}

RISK_THRESHOLDS = [
    (80, RiskLevel.LOW),
    (60, RiskLevel.MEDIUM),
    (40, RiskLevel.HIGH),
    (0,  RiskLevel.CRITICAL),
]


def _score_to_risk(score: int) -> RiskLevel:
    for threshold, level in RISK_THRESHOLDS:
        if score >= threshold:
            return level
    return RiskLevel.CRITICAL


def compute_risk(result: ScanResult) -> Tuple[int, RiskLevel, List[SecurityIssue], List[str]]:
    """Compute weighted security score and generate issues list."""
    score = 100
    issues: List[SecurityIssue] = []
    recommendations: List[str] = []
    issue_id = 1

    # ── Website checks ──────────────────────────────────────────────────────
    if result.website:
        site = result.website
        if not site.reachable:
            score -= 20
            issues.append(SecurityIssue(
                id=f"WEB-{issue_id:03d}", title="Site Unreachable",
                severity=Severity.CRITICAL,
                description="Target website could not be reached.",
                technical_detail="No HTTP/HTTPS response received.",
                remediation="Verify DNS records and server availability.",
                owasp_mapping="A05:2021 - Security Misconfiguration",
                affected_component="Website",
            ))
            issue_id += 1

        if not site.https:
            score -= SEVERITY_WEIGHTS[Severity.HIGH]
            issues.append(SecurityIssue(
                id=f"WEB-{issue_id:03d}", title="No HTTPS",
                severity=Severity.HIGH,
                description="Site not served over HTTPS. Traffic is unencrypted.",
                technical_detail="HTTP connection detected without TLS.",
                remediation="Install SSL certificate and redirect HTTP → HTTPS.",
                owasp_mapping="A02:2021 - Cryptographic Failures",
                affected_component="Transport Security",
            ))
            recommendations.append("Enable HTTPS and redirect all HTTP traffic.")
            issue_id += 1

    # ── Header checks ────────────────────────────────────────────────────────
    if result.headers:
        for h in result.headers:
            if not h.present and h.severity not in (Severity.INFO,):
                deduction = SEVERITY_WEIGHTS.get(h.severity, 0)
                score -= deduction
                issues.append(SecurityIssue(
                    id=f"HDR-{issue_id:03d}",
                    title=f"Missing Header: {h.header}",
                    severity=h.severity,
                    description=h.issue,
                    technical_detail=f"HTTP response missing '{h.header}' header.",
                    remediation=h.remediation,
                    owasp_mapping=h.owasp,
                    affected_component="HTTP Headers",
                ))
                recommendations.append(h.remediation)
                issue_id += 1
            elif h.present and h.severity not in (Severity.INFO,) and "Insecure" in h.issue:
                score -= SEVERITY_WEIGHTS.get(h.severity, 0) // 2
                issues.append(SecurityIssue(
                    id=f"HDR-{issue_id:03d}",
                    title=f"Misconfigured: {h.header}",
                    severity=h.severity,
                    description=h.issue,
                    technical_detail=f"'{h.header}' present but misconfigured.",
                    remediation=h.remediation,
                    owasp_mapping=h.owasp,
                    affected_component="HTTP Headers",
                ))
                issue_id += 1

    # ── SSL checks ───────────────────────────────────────────────────────────
    if result.ssl:
        ssl = result.ssl
        if not ssl.has_ssl:
            score -= SEVERITY_WEIGHTS[Severity.HIGH]
            issues.append(SecurityIssue(
                id=f"SSL-{issue_id:03d}", title="No SSL/TLS",
                severity=Severity.HIGH,
                description="No SSL certificate found on port 443.",
                technical_detail="TLS handshake failed or port 443 not open.",
                remediation="Install a valid SSL certificate (Let's Encrypt is free).",
                owasp_mapping="A02:2021 - Cryptographic Failures",
                affected_component="SSL/TLS",
            ))
            issue_id += 1
        else:
            if ssl.expired:
                score -= SEVERITY_WEIGHTS[Severity.CRITICAL]
                issues.append(SecurityIssue(
                    id=f"SSL-{issue_id:03d}", title="Expired SSL Certificate",
                    severity=Severity.CRITICAL,
                    description="SSL certificate has expired. Browsers will show security warnings.",
                    technical_detail=f"Certificate expired: {ssl.expires}",
                    remediation="Renew SSL certificate immediately.",
                    owasp_mapping="A02:2021 - Cryptographic Failures",
                    affected_component="SSL/TLS",
                ))
                issue_id += 1
            elif ssl.days_remaining and ssl.days_remaining < 30:
                score -= SEVERITY_WEIGHTS[Severity.MEDIUM]
                issues.append(SecurityIssue(
                    id=f"SSL-{issue_id:03d}", title="SSL Expiring Soon",
                    severity=Severity.MEDIUM,
                    description=f"Certificate expires in {ssl.days_remaining} days.",
                    technical_detail=f"Expiry date: {ssl.expires}",
                    remediation="Renew certificate before expiry to avoid downtime.",
                    owasp_mapping="A02:2021 - Cryptographic Failures",
                    affected_component="SSL/TLS",
                ))
                issue_id += 1

            if ssl.self_signed:
                score -= SEVERITY_WEIGHTS[Severity.HIGH]
                issues.append(SecurityIssue(
                    id=f"SSL-{issue_id:03d}", title="Self-Signed Certificate",
                    severity=Severity.HIGH,
                    description="Self-signed certificates are not trusted by browsers.",
                    technical_detail=f"Issuer matches subject: {ssl.issuer}",
                    remediation="Replace with a CA-signed certificate.",
                    owasp_mapping="A02:2021 - Cryptographic Failures",
                    affected_component="SSL/TLS",
                ))
                issue_id += 1

    # ── Port checks ──────────────────────────────────────────────────────────
    if result.ports:
        high_risk_ports = {21, 3306, 5432}
        medium_risk_ports = {25, 8080}
        for p in result.ports:
            if p.open:
                if p.port in high_risk_ports:
                    score -= SEVERITY_WEIGHTS[Severity.HIGH]
                    issues.append(SecurityIssue(
                        id=f"PRT-{issue_id:03d}",
                        title=f"Dangerous Port Open: {p.port}/{p.service}",
                        severity=Severity.HIGH,
                        description=f"Port {p.port} ({p.service}) exposed publicly.",
                        technical_detail=p.notes,
                        remediation=f"Close port {p.port} or restrict via firewall.",
                        owasp_mapping="A05:2021 - Security Misconfiguration",
                        affected_component="Network Ports",
                    ))
                    issue_id += 1
                elif p.port in medium_risk_ports:
                    score -= SEVERITY_WEIGHTS[Severity.MEDIUM]
                    issues.append(SecurityIssue(
                        id=f"PRT-{issue_id:03d}",
                        title=f"Risky Port Open: {p.port}/{p.service}",
                        severity=Severity.MEDIUM,
                        description=f"Port {p.port} ({p.service}) may expose attack surface.",
                        technical_detail=p.notes,
                        remediation=f"Review necessity of port {p.port} and restrict if unused.",
                        owasp_mapping="A05:2021 - Security Misconfiguration",
                        affected_component="Network Ports",
                    ))
                    issue_id += 1

    # Clamp score
    score = max(0, min(100, score))
    risk = _score_to_risk(score)

    logger.info(f"Risk computed: score={score} risk={risk} issues={len(issues)}")
    return score, risk, issues, list(set(recommendations))
