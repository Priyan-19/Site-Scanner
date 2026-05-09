"""
SiteScanner Core - In-Memory Store
Thread-safe temporary scan storage. No database needed.
"""
import asyncio
from typing import Dict, Optional, List
from collections import OrderedDict
from app.models import ScanResult, ScanSummary
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger("store")
settings = get_settings()


class ScanStore:
    """Thread-safe in-memory scan result storage with max-size eviction."""

    def __init__(self, max_size: int = 100):
        self._store: OrderedDict[str, ScanResult] = OrderedDict()
        self._max_size = max_size
        self._lock = asyncio.Lock()

    async def save(self, result: ScanResult) -> None:
        async with self._lock:
            if result.scan_id in self._store:
                self._store.move_to_end(result.scan_id)
            elif len(self._store) >= self._max_size:
                evicted = self._store.popitem(last=False)
                logger.debug(f"Evicted old scan: {evicted[0]}")
            self._store[result.scan_id] = result

    async def get(self, scan_id: str) -> Optional[ScanResult]:
        async with self._lock:
            return self._store.get(scan_id)

    async def history(self) -> List[ScanSummary]:
        async with self._lock:
            summaries = []
            for r in reversed(list(self._store.values())):
                summaries.append(ScanSummary(
                    scan_id=r.scan_id,
                    target=r.target,
                    status=r.status,
                    security_score=r.security_score,
                    risk_level=r.risk_level,
                    timestamp=r.timestamp,
                    scan_duration=r.scan_duration,
                ))
            return summaries

    async def delete(self, scan_id: str) -> bool:
        async with self._lock:
            if scan_id in self._store:
                del self._store[scan_id]
                return True
            return False

    def __len__(self) -> int:
        return len(self._store)


# Global singleton store
scan_store = ScanStore(max_size=settings.max_scan_history)
