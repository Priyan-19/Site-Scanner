"""
SiteScanner Core - Logging
Colored, structured terminal output for developer experience.
"""
import logging
import sys
from app.config import get_settings

try:
    import colorlog
    import colorama
    colorama.init()
    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False


def setup_logging() -> logging.Logger:
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    if HAS_COLORLOG:
        handler = colorlog.StreamHandler(sys.stdout)
        handler.setFormatter(colorlog.ColoredFormatter(
            fmt="%(log_color)s%(asctime)s%(reset)s | %(log_color)s%(levelname)-8s%(reset)s | %(cyan)s%(name)s%(reset)s | %(message)s",
            datefmt="%H:%M:%S",
            log_colors={
                "DEBUG":    "white",
                "INFO":     "green",
                "WARNING":  "yellow",
                "ERROR":    "red",
                "CRITICAL": "bold_red",
            }
        ))
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S"
        ))

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    # Silence noisy libs
    for lib in ["httpx", "httpcore", "uvicorn.access"]:
        logging.getLogger(lib).setLevel(logging.WARNING)

    return logging.getLogger("sitescanner")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"sitescanner.{name}")
