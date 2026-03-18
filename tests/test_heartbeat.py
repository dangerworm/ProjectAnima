"""Tests for Heartbeat."""

from __future__ import annotations

import time

from anima.core.heartbeat import ACTIVE, DORMANT, Heartbeat


def test_pulse_records_heartbeat(tmp_db) -> None:
    hb = Heartbeat(tmp_db)
    hb.pulse(ACTIVE)
    last = tmp_db.get_last_heartbeat()
    assert last is not None
    assert last["status"] == ACTIVE


def test_set_dormant(tmp_db) -> None:
    hb = Heartbeat(tmp_db)
    hb.set_dormant()
    assert hb.status == DORMANT
    last = tmp_db.get_last_heartbeat()
    assert last["status"] == DORMANT


def test_set_active_after_dormant(tmp_db) -> None:
    hb = Heartbeat(tmp_db)
    hb.set_dormant()
    hb.set_active()
    assert hb.status == ACTIVE


def test_last_seen_none_before_first_pulse(tmp_db) -> None:
    hb = Heartbeat(tmp_db)
    # No pulse has been emitted yet
    assert hb.last_seen() is None


def test_start_and_stop(tmp_db) -> None:
    hb = Heartbeat(tmp_db, interval=100)
    hb.start()
    assert hb.last_seen() is not None  # start() emits an immediate pulse
    hb.stop()
