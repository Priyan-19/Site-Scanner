# Manual Running Instructions

Follow these steps to run the Web Vulnerability Scanner on your local machine.

## Prerequisites
-   **Python 3.10+** (for the backend)
-   **Node.js 18+** (for the frontend)

---

## 1. Start the Backend (FastAPI)

1.  Open a terminal and navigate to the `backend` directory:
    ```bash
    cd "backend"
    ```
2.  Activate the virtual environment:
    ```powershell
    # Windows
    .\venv\Scripts\activate
    ```
3.  Install dependencies (if not already installed):
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the backend server:
    ```powershell
    # Recommended for Windows to handle unicode characters:
    $env:PYTHONIOENCODING="utf-8"
    python run.py
    ```
    The backend will be available at [http://localhost:8000](http://localhost:8000).

---

## 2. Start the Frontend (SvelteKit)

1.  Open a **new** terminal and navigate to the `frontend` directory:
    ```bash
    cd "frontend"
    ```
2.  Install dependencies (if not already installed):
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
    The dashboard will be available at [http://localhost:5173/](http://localhost:5173/).

---

## 3. Usage
1.  Open your browser to [http://localhost:5173/](http://localhost:5173/).
2.  Enter a domain (e.g., `google.com`) and click **Start Scan**.
3.  Wait for the real-time progress to complete.
4.  View results and click **Download PDF Report** to save your findings.
