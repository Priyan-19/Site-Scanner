# Product Requirements Document (PRD): SiteScanner Platform

## 1. Product Overview
**SiteScanner** is a production-ready, automated web vulnerability platform designed to provide security professionals and developers with rapid, actionable intelligence about their external attack surface. It transforms complex security probes into a simple, human-readable security score, an interactive dashboard, and a detailed PDF report.

---

## 2. Target Audience
*   **Security Researchers**: For rapid reconnaissance of targets.
*   **DevOps/SREs**: To monitor infrastructure for accidental exposures.
*   **IT Administrators**: To perform basic security hygiene checks on organizational assets.

---

## 3. Key Functional Requirements

### 3.1 Scanning Capabilities (SiteScanner Core)
*   **Network Intelligence**:
    *   TCP Port scanning for common services (80, 443, 21, 22, 3306, etc.).
    *   WHOIS data retrieval (Registrar, Expiry, Age).
    *   DNS record mapping (A, MX, TXT).
*   **Web Security**:
    *   HTTP security header analysis (HSTS, CSP, X-Frame-Options, etc.).
    *   SSL/TLS certificate validation and expiry monitoring.
    *   Passive subdomain discovery.
*   **Risk Engine**:
    *   Automated "Security Score" (0-100) based on weighted deductions.
    *   Categorization of findings into Risk Levels (Low, Medium, High, Critical).
    *   Mapping findings to **OWASP Top 10** categories.

### 3.2 Frontend Dashboard (SiteScanner UI)
*   **Real-time Visualization**: Live WebSocket-driven scan progress and terminal logs.
*   **Data Dashboards**: Visual charts for risk distribution and category analysis.
*   **History Management**: Persistent list of previous scans with search and reload functionality.
*   **Exportable Reports**: In-browser report preview and downloadable professional PDF summaries.

---

## 4. Technical Architecture

### 4.1 Backend Engine
*   **Language**: Python 3.14+
*   **API Framework**: FastAPI (Asynchronous)
*   **Concurrency**: `asyncio` for parallel scanner execution to minimize scan time.
*   **Security**: Rate limiting via `slowapi` and strict Pydantic domain validation.

### 4.2 Frontend Application
*   **Framework**: SvelteKit (Svelte 5)
*   **Language**: TypeScript
*   **Styling**: TailwindCSS v4 (Design System driven)
*   **State Management**: Runes-based reactive state for real-time updates.

---

## 5. Implementation Status

### ✅ Phase 1: Core Engine (Completed)
- [x] Website, Headers, SSL, WHOIS, Ports, Subdomains scanners.
- [x] Weighted risk scoring engine.
- [x] Automated PDF report generation (ReportLab).

### ✅ Phase 2: Modern Dashboard (Completed)
- [x] SvelteKit + Tailwind 4 implementation.
- [x] WebSocket integration for real-time logs.
- [x] Responsive enterprise UI with glassmorphism.

### 🔄 Phase 3: Future Roadmap
- [ ] **Advanced Crawling**: Deep path discovery and hidden file detection.
- [ ] **Tech Profiling**: Passive technology stack detection (CMS, Frameworks).
- [ ] **Database Integration**: Persistent PostgreSQL storage for long-term historical trends.
- [ ] **CVE Integration**: Mapping findings to known Common Vulnerabilities and Exposures.

---

## 6. Design Philosophy
## 6. Performance & Security Targets

### 6.1 Performance Benchmarks
*   **Scan Duration**: Complete reconnaissance scan (Headers, SSL, WHOIS, Ports, Subdomains) should finish in **< 30 seconds** for average domains.
*   **Concurrency**: Support up to **50 concurrent scans** without degradation in response time (scaled via worker nodes).
*   **Real-time Latency**: WebSocket updates should have a latency of **< 200ms** from finding discovery to UI update.

### 6.2 Security Constraints
*   **Sanitization**: All backend results (WHOIS, Banner grabs) must be sanitized on the frontend to prevent XSS.
*   **Rate Limiting**: Enforce a strict limit of **5 scans per minute per IP** to prevent infrastructure abuse.
*   **Network Privacy**: All scans are executed from the server backend; client IP is never exposed to the target domain.

## 7. UI/UX Design Requirements

### 7.1 Aesthetic Guidelines
*   **Color Palette**: White (#FFFFFF) base, Slate (#64748B) text, and Primary Blue (#0066FF) accents.
*   **Typography**: Inter (Sans-serif) for high readability in technical data.
*   **Feedback**: Use skeleton loaders for async data and smooth transitions for state changes.

### 7.2 Accessibility
*   **Contrast**: Maintain WCAG AA standard contrast ratios for all text and icons.
*   **Responsiveness**: 100% functional on mobile devices with collapsible navigation and scrollable data tables.

## 8. Ethical Considerations
SiteScanner enforces ethical usage by providing warnings and emphasizing authorized testing. It uses passive/low-noise scanning techniques to remain non-disruptive to production environments.

---

## 9. Project Structure & File Descriptions

### 📂 Root Directory
*   `PRD.md`: This document (Product Requirements Document).
*   `README.md`: Project overview, setup instructions, and architecture.
*   `RUN_MANUALLY.md`: Detailed instructions for running the system without automation scripts.

### 🐍 Backend (`/backend`)
*   `run.py`: Entry point script to launch the FastAPI server.
*   `requirements.txt`: Python dependencies (FastAPI, ReportLab, Whois, etc.).
*   `.env`: Environment variables configuration.
*   `app/main.py`: FastAPI application initialization and middleware configuration.
*   `app/config/settings.py`: Configuration management using Pydantic Settings.
*   `app/core/logging.py`: Custom logging system for backend events.
*   `app/core/store.py`: In-memory volatile storage for scan results.
*   `app/middleware/error_handler.py`: Global exception handling and standardized error responses.
*   `app/models/scan.py`: Pydantic schemas for API requests and response validation.
*   `app/reports/pdf_generator.py`: Generates professional PDF reports from scan data.
*   `app/routes/scan_routes.py`: REST endpoints for scan initiation and report retrieval.
*   `app/routes/ws_routes.py`: WebSocket handlers for real-time progress broadcasting.
*   `app/scanners/`: Individual scanning modules (Headers, SSL, Ports, Whois, etc.).
*   `app/services/scan_service.py`: Main orchestration engine for running scanners.
*   `app/services/risk_engine.py`: Logic for scoring and risk assessment.
*   `app/websocket/manager.py`: Connection manager for real-time client updates.

### ⚡ Frontend (`/frontend`)
*   `package.json`: NPM dependencies and build scripts (SvelteKit, Tailwind 4).
*   `svelte.config.js` / `vite.config.ts`: Configuration for SvelteKit and Vite.
*   `src/app.html`: Main HTML template.
*   `src/routes/+layout.svelte`: Global layout, including navigation and toast notifications.
*   `src/routes/+page.svelte`: Main interactive scan dashboard.
*   `src/routes/history/+page.svelte`: Historical scan management interface.
*   `src/routes/report/+page.svelte`: Detailed post-scan analysis view.
*   `src/lib/api/`: API clients for REST (`scan.ts`) and WebSockets (`websocket.ts`).
*   `src/lib/components/`: Modular UI components (Charts, Gauges, Inputs, Tables).
*   `src/lib/stores/`: Svelte 5 Rune stores for state management (`scanStore.svelte.ts`, etc.).
*   `src/lib/utils/`: Utility functions for data formatting and sanitization.

---
*Last Updated: May 09, 2026*
