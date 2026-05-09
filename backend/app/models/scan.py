"""
SiteScanner Core - Pydantic Models
Strongly typed data models for all scan structures.
"""
from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


# ─── Enums ────────────────────────────────────────────────────────────────────

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ScanStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ─── Sub-models ───────────────────────────────────────────────────────────────

class SecurityIssue(BaseModel):
    id: str
    title: str
    severity: Severity
    description: str
    technical_detail: str
    remediation: str
    owasp_mapping: str
    affected_component: str


class HeaderAnalysis(BaseModel):
    header: str
    present: bool
    value: Optional[str] = None
    severity: Severity
    issue: str
    remediation: str
    owasp: str


class PortResult(BaseModel):
    port: int
    open: bool
    service: str
    risk: str
    notes: str


class SSLResult(BaseModel):
    has_ssl: bool
    valid: bool
    issuer: Optional[str] = None
    subject: Optional[str] = None
    expires: Optional[str] = None
    days_remaining: Optional[int] = None
    tls_version: Optional[str] = None
    self_signed: bool = False
    expired: bool = False
    issues: List[str] = []


class WhoisResult(BaseModel):
    domain: str
    registrar: Optional[str] = None
    creation_date: Optional[str] = None
    expiration_date: Optional[str] = None
    domain_age_days: Optional[int] = None
    name_servers: List[str] = []
    dns_records: Dict[str, List[str]] = {}
    error: Optional[str] = None


class SubdomainResult(BaseModel):
    subdomain: str
    full_domain: str
    reachable: bool
    ip: Optional[str] = None
    status_code: Optional[int] = None


class WebsiteInfo(BaseModel):
    url: str
    status_code: Optional[int] = None
    https: bool = False
    redirect_chain: List[str] = []
    final_url: Optional[str] = None
    server: Optional[str] = None
    content_type: Optional[str] = None
    response_time_ms: Optional[float] = None
    reachable: bool = False


# ─── Main Scan Models ─────────────────────────────────────────────────────────

class ScanRequest(BaseModel):
    target: str
    include_ports: bool = True
    include_whois: bool = True
    include_subdomains: bool = True
    include_ssl: bool = True

    @field_validator("target")
    @classmethod
    def validate_target(cls, v: str) -> str:
        v = v.strip().lower()
        # Strip protocol for storage; scanner normalizes
        v = v.replace("https://", "").replace("http://", "").rstrip("/")
        if not v or len(v) < 3:
            raise ValueError("Invalid target domain")
        # Basic domain check
        import re
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
        if not re.match(pattern, v):
            raise ValueError("Target must be a valid domain (e.g. example.com)")
        return v


class ScanResult(BaseModel):
    scan_id: str
    target: str
    status: ScanStatus
    security_score: Optional[int] = None
    risk_level: Optional[RiskLevel] = None
    website: Optional[WebsiteInfo] = None
    headers: Optional[List[HeaderAnalysis]] = None
    ports: Optional[List[PortResult]] = None
    ssl: Optional[SSLResult] = None
    whois: Optional[WhoisResult] = None
    subdomains: Optional[List[SubdomainResult]] = None
    issues: List[SecurityIssue] = []
    recommendations: List[str] = []
    scan_duration: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    error: Optional[str] = None
    progress: int = 0
    current_stage: Optional[str] = None


class ScanSummary(BaseModel):
    scan_id: str
    target: str
    status: ScanStatus
    security_score: Optional[int] = None
    risk_level: Optional[RiskLevel] = None
    timestamp: datetime
    scan_duration: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    app_name: str
    timestamp: datetime = datetime.utcnow()
