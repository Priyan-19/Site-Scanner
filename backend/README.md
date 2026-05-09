# 🛡 SiteScanner Core

**Production-grade defensive cybersecurity scanning engine built with Python FastAPI.**

> ⚠️ **Ethical Use Only.** Only scan domains you own or have explicit written permission to test. This tool is designed for defensive security auditing and education only.

---

## Features

| Module | Description | Technical Implementation |
|---|---|---|
| 🌐 Website Analysis | HTTP/HTTPS status, redirects, timing | `httpx.AsyncClient` with custom UA strings |
| 🔒 Security Headers | CSP, HSTS, X-Frame-Options audit | Regex-based policy validation & OWASP mapping |
| 🔌 Port Scanner | Parallel TCP connect scan | `ThreadPoolExecutor` (Max 100 workers) |
| 🔑 SSL/TLS | Cert validation, expiry, cipher suites | Python `ssl` module + `OpenSSL` |
| 📋 WHOIS & DNS | Ownership, expiry, A/MX/TXT records | `python-whois` + `dnspython` |
| 🔍 Subdomain Enum | Passive DNS-based detection | Common wordlist + passive DNS lookups |
| 📊 Risk Engine | Weighted 0-100 scoring algorithm | Severity-based deductions (Critical: -25, High: -15) |
| 📡 WebSocket | Real-time scan progress streaming | FastAPI `WebSocket` manager with pub/sub |
| 📄 PDF Reports | Branded security reports | `ReportLab` Canvas & Platypus engine |

### 🧠 Risk Calculation Logic
The security score starts at **100** and is calculated using a weighted deduction model:
- **Critical Issues**: -25 points (e.g., Expired SSL, Open Database Ports)
- **High Issues**: -15 points (e.g., Missing HSTS, Sensitive Ports)
- **Medium Issues**: -7 points (e.g., Missing CSP, X-Frame-Options)
- **Low Issues**: -2 points (e.g., Info headers, Server banners)
- **Minimum Score**: 0 (Calculated results are clamped)

### ⚡ Concurrency Model
To ensure rapid execution, SiteScanner uses a hybrid concurrency model:
1. **Asyncio**: Orchestrates all scanners in parallel.
2. **ThreadPoolExecutor**: Offloads blocking I/O (like Port Scanning and WHOIS) to prevent event loop blocking.
3. **HTTP Pooling**: Reuses connections via `httpx.AsyncClient`.

---

## Quick Start

### 1. Clone / Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env as needed
```

### 3. Run

```bash
python run.py
# or with hot reload:
DEBUG=true python run.py
```

Server starts at: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

---

## API Reference

### `POST /api/v1/scan` — Start a Scan

```bash
curl -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com"}'
```

**Response:**
```json
{
  "scan_id": "uuid-here",
  "target": "example.com",
  "status": "running",
  "message": "Scan started. Poll GET /scan/{scan_id} for results.",
  "websocket": "/ws/scan/uuid-here"
}
```

---

### `GET /api/v1/scan/{scan_id}` — Get Results

```bash
curl http://localhost:8000/api/v1/scan/{scan_id}
```

**Response:**
```json
{
  "scan_id": "...",
  "target": "example.com",
  "status": "completed",
  "security_score": 72,
  "risk_level": "MEDIUM",
  "website": {...},
  "headers": [...],
  "ports": [...],
  "ssl": {...},
  "whois": {...},
  "subdomains": [...],
  "issues": [...],
  "recommendations": [...],
  "scan_duration": "18.32s",
  "timestamp": "..."
}
```

---

### `GET /api/v1/history` — Scan History

```bash
curl http://localhost:8000/api/v1/history
```

---

### `GET /api/v1/report/{scan_id}` — Download Report

```bash
# PDF report
curl -o report.pdf "http://localhost:8000/api/v1/report/{scan_id}"

# JSON report
curl -o report.json "http://localhost:8000/api/v1/report/{scan_id}?format=json"
```

---

### `GET /api/v1/health` — Health Check

```bash
curl http://localhost:8000/api/v1/health
```

---

### WebSocket — Real-Time Progress

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/scan/{scan_id}");

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // { type: "progress", stage: "SSL/TLS Inspection", progress: 40 }
  // { type: "complete", security_score: 72, risk_level: "MEDIUM" }
  // { type: "error", error: "..." }
};
```

---

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI app factory + lifespan
│   ├── config/
│   │   └── settings.py      # Pydantic-settings config
│   ├── routes/
│   │   ├── scan_routes.py   # REST endpoints
│   │   └── ws_routes.py     # WebSocket endpoint
│   ├── services/
│   │   ├── scan_service.py  # Scan orchestrator
│   │   └── risk_engine.py   # Weighted scoring engine
│   ├── scanners/
│   │   ├── website.py       # HTTP analysis
│   │   ├── headers.py       # Security headers
│   │   ├── ports.py         # Port scanner (ThreadPoolExecutor)
│   │   ├── ssl_scanner.py   # SSL/TLS inspection
│   │   ├── whois_scanner.py # WHOIS + DNS
│   │   └── subdomains.py    # Passive subdomain enum
│   ├── websocket/
│   │   └── manager.py       # WS connection manager
│   ├── models/
│   │   └── scan.py          # Pydantic models
│   ├── reports/
│   │   └── pdf_generator.py # ReportLab PDF
│   ├── core/
│   │   ├── store.py         # In-memory scan store
│   │   └── logging.py       # Colored logging
│   └── middleware/
│       └── error_handler.py # Global error handling
├── run.py                   # Entry point
├── requirements.txt
├── .env
└── README.md
```

---

## Configuration (.env)

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | SiteScanner Core | App name |
| `DEBUG` | false | Hot reload |
| `HOST` | 0.0.0.0 | Bind address |
| `PORT` | 8000 | Port |
| `SCAN_TIMEOUT` | 60 | HTTP timeout (s) |
| `PORT_SCAN_TIMEOUT` | 1 | TCP timeout (s) |
| `MAX_SCAN_HISTORY` | 100 | In-memory scan limit |
| `ALLOWED_ORIGINS` | localhost:3000,... | CORS origins |

---

## Ethical Restrictions

This tool is:
- ✅ Defensive only
- ✅ Educational
- ✅ Passive scanning
- ❌ No exploit execution
- ❌ No brute force
- ❌ No credential attacks
- ❌ No malware functionality
- ❌ No payload injection

---

## License

MIT. Use responsibly.
