"""Shared fixtures for Project Anima tests."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from anima.settings import Settings
from anima.storage.database import Database


@pytest.fixture()
def tmp_db(tmp_path: Path) -> Database:
    """A fresh in-memory-equivalent SQLite database in a temp directory."""
    return Database(tmp_path / "test_anima.db")


@pytest.fixture()
def test_settings(tmp_path: Path) -> Settings:
    """Settings that point at a throwaway data directory."""
    return Settings(data_dir=tmp_path, llm_api_key="", heartbeat_interval=9999)
