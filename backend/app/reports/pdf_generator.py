"""
SiteScanner Core - PDF Report Generator
Professional security report via ReportLab.
"""
import io
from datetime import datetime, timedelta
from typing import Optional
from app.models import ScanResult, RiskLevel, Severity
from app.core.logging import get_logger

logger = get_logger("reports.pdf")

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    logger.warning("ReportLab not installed; PDF generation disabled")

# Color palette
COLORS = {
    "primary":   colors.HexColor("#1a1a2e"),
    "accent":    colors.HexColor("#0f3460"),
    "success":   colors.HexColor("#16a34a"),
    "warning":   colors.HexColor("#d97706"),
    "danger":    colors.HexColor("#dc2626"),
    "critical":  colors.HexColor("#7c3aed"),
    "info":      colors.HexColor("#2563eb"),
    "light_bg":  colors.HexColor("#f8fafc"),
    "border":    colors.HexColor("#e2e8f0"),
    "white":     colors.white,
}

RISK_COLORS = {
    RiskLevel.LOW:      COLORS["success"],
    RiskLevel.MEDIUM:   COLORS["warning"],
    RiskLevel.HIGH:     COLORS["danger"],
    RiskLevel.CRITICAL: COLORS["critical"],
}

SEVERITY_COLORS = {
    Severity.INFO:     COLORS["info"],
    Severity.LOW:      COLORS["success"],
    Severity.MEDIUM:   COLORS["warning"],
    Severity.HIGH:     COLORS["danger"],
    Severity.CRITICAL: COLORS["critical"],
}


def generate_pdf(result: ScanResult) -> bytes:
    if not HAS_REPORTLAB:
        raise RuntimeError("ReportLab not installed. Run: pip install reportlab")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Styles ────────────────────────────────────────────────────────────────
    title_style = ParagraphStyle("title", fontSize=26, textColor=COLORS["primary"],
                                  spaceAfter=12, alignment=TA_CENTER, fontName="Helvetica-Bold")
    sub_style = ParagraphStyle("sub", fontSize=12, textColor=COLORS["accent"],
                                spaceAfter=10, alignment=TA_CENTER)
    h2_style = ParagraphStyle("h2", fontSize=14, textColor=COLORS["primary"],
                               spaceBefore=14, spaceAfter=6, fontName="Helvetica-Bold")
    body_style = ParagraphStyle("body", fontSize=9, textColor=colors.HexColor("#374151"),
                                 spaceAfter=4, leading=14)
    small_style = ParagraphStyle("small", fontSize=8, textColor=colors.HexColor("#6b7280"),
                                  spaceAfter=2)

    # ── Cover ─────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("SITESCANNER CORE", title_style))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("SECURITY ASSESSMENT REPORT", sub_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=COLORS["accent"]))
    story.append(Spacer(1, 1*cm))

    # Target + score table
    risk_color = RISK_COLORS.get(result.risk_level, COLORS["info"])
    score_display = str(result.security_score) if result.security_score is not None else "N/A"
    risk_display = result.risk_level.value if result.risk_level else "N/A"

    cover_data = [
        ["Target", result.target],
        ["Security Score", f"{score_display} / 100"],
        ["Risk Level", risk_display],
        ["Scan Status", result.status.value.upper()],
        ["Timestamp", (result.timestamp + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M IST")],
        ["Duration", result.scan_duration or "N/A"],
    ]

    cover_table = Table(cover_data, colWidths=[4*cm, 12*cm])
    cover_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [COLORS["light_bg"], COLORS["white"]]),
        ("GRID", (0, 0), (-1, -1), 0.5, COLORS["border"]),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("TEXTCOLOR", (1, 1), (1, 1), COLORS["accent"]),
        ("TEXTCOLOR", (1, 2), (1, 2), risk_color),
        ("FONTNAME", (1, 2), (1, 2), "Helvetica-Bold"),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Issues Summary ────────────────────────────────────────────────────────
    if result.issues:
        story.append(Paragraph("Security Issues Found", h2_style))
        issue_data = [["ID", "Title", "Severity", "Component"]]
        for issue in result.issues:
            sev_str = issue.severity.value
            issue_data.append([
                issue.id,
                issue.title[:50],
                sev_str,
                issue.affected_component,
            ])

        issue_table = Table(issue_data, colWidths=[2*cm, 7*cm, 2.5*cm, 4.5*cm])
        sev_colors_ts = []
        for i, issue in enumerate(result.issues, start=1):
            c = SEVERITY_COLORS.get(issue.severity, COLORS["info"])
            sev_colors_ts.append(("TEXTCOLOR", (2, i), (2, i), c))
            sev_colors_ts.append(("FONTNAME", (2, i), (2, i), "Helvetica-Bold"))

        issue_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COLORS["primary"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), COLORS["white"]),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLORS["light_bg"], COLORS["white"]]),
            ("GRID", (0, 0), (-1, -1), 0.5, COLORS["border"]),
            ("PADDING", (0, 0), (-1, -1), 5),
        ] + sev_colors_ts))
        story.append(issue_table)
        story.append(Spacer(1, 0.3*cm))

    # ── Detailed Issues ───────────────────────────────────────────────────────
    if result.issues:
        story.append(Paragraph("Detailed Findings", h2_style))
        for issue in result.issues:
            c = SEVERITY_COLORS.get(issue.severity, COLORS["info"])
            detail_data = [
                [f"[{issue.id}] {issue.title}"],
                [f"Severity: {issue.severity.value}  |  Component: {issue.affected_component}"],
                [f"Description: {issue.description}"],
                [f"Technical: {issue.technical_detail}"],
                [f"Remediation: {issue.remediation}"],
                [f"OWASP: {issue.owasp_mapping}"],
            ]
            t = Table(detail_data, colWidths=[16*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), c),
                ("TEXTCOLOR", (0, 0), (-1, 0), COLORS["white"]),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLORS["light_bg"], COLORS["white"]]),
                ("GRID", (0, 0), (-1, -1), 0.5, COLORS["border"]),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(KeepTogether([t, Spacer(1, 0.2*cm)]))

    # ── Recommendations ───────────────────────────────────────────────────────
    if result.recommendations:
        story.append(Paragraph("Recommendations", h2_style))
        for i, rec in enumerate(result.recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", body_style))

    # ── SSL Summary ───────────────────────────────────────────────────────────
    if result.ssl:
        story.append(Paragraph("SSL/TLS Summary", h2_style))
        ssl = result.ssl
        ssl_data = [
            ["Has SSL", "Yes" if ssl.has_ssl else "No"],
            ["Valid", "Yes" if ssl.valid else "No"],
            ["Issuer", ssl.issuer or "N/A"],
            ["Expires", ssl.expires or "N/A"],
            ["Days Remaining", str(ssl.days_remaining) if ssl.days_remaining is not None else "N/A"],
            ["TLS Version", ssl.tls_version or "N/A"],
        ]
        ssl_table = Table(ssl_data, colWidths=[4*cm, 12*cm])
        ssl_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [COLORS["light_bg"], COLORS["white"]]),
            ("GRID", (0, 0), (-1, -1), 0.5, COLORS["border"]),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(ssl_table)

    # ── Port Scanning ─────────────────────────────────────────────────────────
    if result.ports:
        story.append(Paragraph("Open Ports & Services", h2_style))
        port_data = [["Port", "Service", "Status", "Risk", "Notes"]]
        for p in result.ports:
            if p.open:
                port_data.append([
                    str(p.port),
                    p.service,
                    "OPEN",
                    p.risk,
                    p.notes
                ])
        
        if len(port_data) > 1:
            port_table = Table(port_data, colWidths=[2*cm, 3*cm, 2*cm, 2*cm, 7*cm])
            port_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), COLORS["accent"]),
                ("TEXTCOLOR", (0, 0), (-1, 0), COLORS["white"]),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLORS["light_bg"], COLORS["white"]]),
                ("GRID", (0, 0), (-1, -1), 0.5, COLORS["border"]),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(port_table)
        else:
            story.append(Paragraph("No open ports detected in common range.", body_style))

    # ── Subdomains ────────────────────────────────────────────────────────────
    if result.subdomains:
        story.append(Paragraph("Subdomain Enumeration", h2_style))
        sub_data = [["Subdomain", "IP Address", "Status"]]
        for s in result.subdomains:
            sub_data.append([
                s.full_domain,
                s.ip or "N/A",
                "REACHABLE" if s.reachable else "UNREACHABLE"
            ])
        
        sub_table = Table(sub_data, colWidths=[8*cm, 4*cm, 4*cm])
        sub_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COLORS["accent"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), COLORS["white"]),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLORS["light_bg"], COLORS["white"]]),
            ("GRID", (0, 0), (-1, -1), 0.5, COLORS["border"]),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(sub_table)

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=COLORS["border"]))
    story.append(Paragraph(
        f"Generated by SiteScanner Core | {(datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M IST')} | Defensive & Educational Use Only",
        small_style
    ))

    doc.build(story)
    return buf.getvalue()
