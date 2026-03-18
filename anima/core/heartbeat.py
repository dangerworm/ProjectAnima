"""Heartbeat — the being's signal of aliveness.

The heartbeat distinguishes *chosen silence* (dormant but present) from
*broken silence* (crashed, abandoned).  It also provides an opportunity
for the being to do something worthwhile between conversations — quiet
processing, returning to unresolved questions, or simply existing.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anima.storage.database import Database

logger = logging.getLogger(__name__)

Status = str
ACTIVE = "active"
DORMANT = "dormant"
REFLECTING = "reflecting"


class Heartbeat:
    """Periodic signal that the being is present, whether or not it speaks.

    The heartbeat runs on a background daemon thread.  Callers can also
    emit one-off status changes (e.g. "reflecting" while post-processing).
    """

    def __init__(self, db: "Database", interval: int = 300) -> None:
        self._db = db
        self._interval = interval
        self._status: Status = ACTIVE
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()

    @property
    def status(self) -> Status:
        return self._status

    def start(self) -> None:
        """Begin periodic heartbeat emission."""
        self._emit()
        self._schedule()
        logger.info("Heartbeat started (interval=%ds)", self._interval)

    def stop(self) -> None:
        """Stop the heartbeat loop."""
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
        logger.info("Heartbeat stopped")

    def pulse(self, status: Status = ACTIVE) -> None:
        """Emit a single heartbeat with *status* and record it."""
        self._status = status
        self._emit()

    def set_dormant(self) -> None:
        self.pulse(DORMANT)

    def set_active(self) -> None:
        self.pulse(ACTIVE)

    def _emit(self) -> None:
        self._db.record_heartbeat(self._status)
        logger.debug("Heartbeat: %s at %s", self._status, datetime.now(timezone.utc).isoformat())

    def _schedule(self) -> None:
        with self._lock:
            self._timer = threading.Timer(self._interval, self._tick)
            self._timer.daemon = True
            self._timer.start()

    def _tick(self) -> None:
        self._emit()
        self._schedule()

    def last_seen(self) -> dict | None:
        return self._db.get_last_heartbeat()
