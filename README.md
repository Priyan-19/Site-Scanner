<div align="center">

# 🛡️ SiteScanner
### Enterprise-Grade Web Vulnerability Assessment Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Svelte](https://img.shields.io/badge/Svelte%205-FF3E00?style=for-the-badge&logo=svelte&logoColor=white)](https://svelte.dev/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS_4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python_3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

**SiteScanner** is a powerful, automated security reconnaissance platform designed to provide a comprehensive view of any web application's external attack surface. It combines high-speed asynchronous scanning with an intelligent risk assessment engine and a premium, real-time dashboard.

[Explore the PRD](PRD.md) · [API Documentation](http://localhost:8000/docs) · [Report a Bug](https://github.com/yourusername/sitescanner/issues)

</div>

---

## 📖 Project Overview

SiteScanner simplifies the complex process of web security auditing. By entering a single URL, users receive a multi-layered analysis covering infrastructure, SSL/TLS health, security headers, and domain information. The platform is built for speed, security, and actionable results.

### Core Value Proposition
- **Automated Intelligence**: No complex configuration required.
- **Real-Time Visibility**: Watch the scan progress via live WebSocket logs.
- **Risk-First Approach**: Immediate clarity on security posture with weighted scoring.
- **Professional Reporting**: Generate high-quality PDF summaries for stakeholders.

---

## 🏗️ System Architecture

SiteScanner follows a modern decoupled architecture:

### 🐍 Backend: FastAPI Engine
The backend is a high-performance Python application built with **FastAPI**. It leverages `asyncio` to run multiple security probes in parallel, ensuring complete scans finish in seconds.
- **Scanners**: Modular probes for Headers, Ports, SSL, Subdomains, and WHOIS.
- **Risk Engine**: Algorithms that translate raw findings into severity levels (Critical to Low).
- **WebSocket Manager**: Broadcasts live status updates and terminal logs to connected clients.

### ⚡ Frontend: Svelte 5 Dashboard
The frontend is a cutting-edge **SvelteKit** application utilizing the latest **Svelte 5 Runes** for state management.
- **Reactive UI**: Instant updates as data arrives via WebSockets.
- **Visual Analytics**: Interactive charts and gauges built with Chart.js.
- **Design System**: A sleek, dark-themed (or light) interface powered by **TailwindCSS 4**.

---

## 📂 Project Structure

```text
.
├── backend/                # Python FastAPI Backend
│   ├── app/                # Core Application Logic
│   │   ├── config/         # App Settings & Environment
│   │   ├── core/           # Logging & Shared Stores
│   │   ├── middleware/     # Global Error Handlers
│   │   ├── models/         # Pydantic Schemas
│   │   ├── reports/        # PDF Generation Logic
│   │   ├── routes/         # API & WebSocket Endpoints
│   │   ├── scanners/       # Individual Security Probes
│   │   ├── services/       # Orchestration & Risk Logic
│   │   └── websocket/      # Connection Management
│   └── run.py              # Server Entry Point
├── frontend/               # SvelteKit Frontend
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api/        # REST & WS Clients
│   │   │   ├── components/ # Reusable UI Components
│   │   │   ├── stores/     # Svelte 5 Rune Stores
│   │   │   └── utils/      # Data Formatters
│   │   └── routes/         # Pages & Layouts
│   └── package.json        # Frontend Dependencies
├── PRD.md                  # Product Requirements Document
└── README.md               # Project Overview (This file)
```

---

## 🚀 Key Features

### 🔍 Deep Reconnaissance
*   **🌐 Website & Header Audit**: Analysis of HTTP/S reachability and security header configuration (CSP, HSTS, etc.).
*   **📡 Infrastructure Intelligence**: Rapid TCP port scanning, WHOIS data retrieval, and DNS record mapping.
*   **🔒 SSL/TLS Validation**: Comprehensive certificate analysis, chain validation, and expiry monitoring.
*   **🔎 Subdomain Discovery**: Passive enumeration to uncover hidden assets.

### 📊 Security Analytics
*   **🎯 Weighted Security Score (0-100)**: Real-time risk computation based on finding severity.
*   **🛡️ OWASP Mapping**: Categorization of vulnerabilities into OWASP Top 10 categories.
*   **📈 Interactive Charts**: Visual risk distribution and historical trends.

---

## 🏁 Getting Started

### 1. Launch the Engine (Backend)
```bash
cd backend
pip install -r requirements.txt
python run.py
```

### 2. Launch the Dashboard (Frontend)
```bash
cd frontend
npm install
npm run dev
```

### 3. Start Scanning
1. Open `http://localhost:5173`
2. Enter your target domain (e.g., `google.com`)
3. Watch the real-time pipeline and export your report!

---

## 🔒 Security & Ethics

> [!IMPORTANT]
> SiteScanner is intended for **authorized security testing only**. You must have explicit permission to scan target infrastructure. The platform is designed for defensive auditing and education.

---

<div align="center">
  <p>Built with ❤️ for a Safer Web</p>
  <p>© 2026 SiteScanner Platform. All Rights Reserved.</p>
</div>
