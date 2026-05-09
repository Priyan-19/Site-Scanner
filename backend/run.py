"""
SiteScanner Core - Entry Point
Run with: python run.py
"""
import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_config=None,  # Use our custom logging
        access_log=False,
    )
