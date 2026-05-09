# SiteScanner Frontend

SiteScanner is a production-grade cybersecurity dashboard built with **SvelteKit**, **TypeScript**, and **TailwindCSS**. It provides real-time web vulnerability scanning visualization with a premium, enterprise-grade interface.

## ✨ Features

- **Real-time Scanning Engine**: Live updates via WebSockets with progress tracking and terminal-style logs.
- **Enterprise Dashboard**: Clean, professional SaaS UI with glassmorphism and modern aesthetics.
- **Security Analytics**: Data-driven visualization using Chart.js for risk distribution and trends.
- **Vulnerability Management**: Interactive findings cards with technical drill-downs and remediation guides.
- **Automated Reporting**: High-fidelity, printable PDF report generation.
- **Scan History**: Full history of previous scans with advanced search and filtering.
- **Mobile Responsive**: Fully optimized for desktop, tablet, and mobile devices.

## 🛠️ Tech Stack

- **Framework**: [SvelteKit](https://kit.svelte.dev/) (Svelte 5)
- **Styling**: [TailwindCSS v4](https://tailwindcss.com/)
- **Icons**: [Lucide Svelte](https://lucide.dev/)
- **Charts**: [Chart.js](https://www.chartjs.org/)
- **State Management**: Svelte 5 Runes ($state, $derived, $props)
- **API Integration**: WebSocket & Fetch API

## 🚀 Getting Started

### Prerequisites

- Node.js 18.x or later
- npm or pnpm

### Installation

1. Install dependencies:

   ```bash
   npm install
   ```

2. Start the development server:

   ```bash
   npm run dev
   ```

3. Open [http://localhost:5173](http://localhost:5173) in your browser.

## 📁 Project Structure

- `src/lib/components`: Reusable UI components (Navbar, RiskGauge, Charts, etc.)
- `src/lib/stores`: Application state (scan, history, toasts)
- `src/lib/api`: Backend service wrappers (REST & WebSocket)
- `src/lib/utils`: Formatting and business logic helpers
- `src/routes`: Application pages and layouts

## 🔒 Security

- **Input Sanitization**: All backend outputs are safely rendered.
- **Strict Typing**: Full TypeScript coverage for API responses.
- **No Sensitive Data**: Zero local storage of credentials or sensitive scan data.

---

© 2026 SiteScanner Inc. Confidential.
