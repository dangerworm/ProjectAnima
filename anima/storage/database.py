"""SQLite persistence layer.

All tables are created lazily on first use so that importing the module
never fails even if the data directory does not yet exist.
"""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


_lock = threading.Lock()


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database:
    """Thread-safe SQLite wrapper for Project Anima data."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._path = str(path)
        self._local = threading.local()
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        if not getattr(self._local, "conn", None):
            conn = sqlite3.connect(self._path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            self._local.conn = conn
        return self._local.conn

    def _init_schema(self) -> None:
        with _lock:
            conn = self._connect()
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS identity (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS conversations (
                    id         TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    ended_at   TEXT,
                    summary    TEXT
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL REFERENCES conversations(id),
                    role            TEXT NOT NULL,
                    content         TEXT NOT NULL,
                    created_at      TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS reflections (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL REFERENCES conversations(id),
                    content         TEXT NOT NULL,
                    created_at      TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS interests (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic      TEXT NOT NULL UNIQUE,
                    strength   REAL NOT NULL DEFAULT 1.0,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS questions (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    content    TEXT NOT NULL,
                    resolved   INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    resolved_at TEXT
                );

                CREATE TABLE IF NOT EXISTS heartbeats (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    status     TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.commit()

    # ------------------------------------------------------------------
    # Identity helpers
    # ------------------------------------------------------------------

    def get_identity(self) -> dict[str, str]:
        conn = self._connect()
        rows = conn.execute("SELECT key, value FROM identity").fetchall()
        return {row["key"]: row["value"] for row in rows}

    def set_identity_field(self, key: str, value: str) -> None:
        with _lock:
            conn = self._connect()
            conn.execute(
                """
                INSERT INTO identity (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
                """,
                (key, value, _utcnow()),
            )
            conn.commit()

    # ------------------------------------------------------------------
    # Conversation helpers
    # ------------------------------------------------------------------

    def create_conversation(self, conversation_id: str) -> None:
        with _lock:
            conn = self._connect()
            conn.execute(
                "INSERT INTO conversations (id, started_at) VALUES (?, ?)",
                (conversation_id, _utcnow()),
            )
            conn.commit()

    def end_conversation(self, conversation_id: str, summary: str | None = None) -> None:
        with _lock:
            conn = self._connect()
            conn.execute(
                "UPDATE conversations SET ended_at=?, summary=? WHERE id=?",
                (_utcnow(), summary, conversation_id),
            )
            conn.commit()

    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        with _lock:
            conn = self._connect()
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (conversation_id, role, content, _utcnow()),
            )
            conn.commit()

    def get_messages(self, conversation_id: str) -> list[dict[str, Any]]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT role, content, created_at FROM messages WHERE conversation_id=? ORDER BY id",
            (conversation_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def get_recent_conversations(self, limit: int = 10) -> list[dict[str, Any]]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT id, started_at, ended_at, summary FROM conversations ORDER BY started_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Reflection helpers
    # ------------------------------------------------------------------

    def add_reflection(self, conversation_id: str, content: str) -> None:
        with _lock:
            conn = self._connect()
            conn.execute(
                "INSERT INTO reflections (conversation_id, content, created_at) VALUES (?, ?, ?)",
                (conversation_id, content, _utcnow()),
            )
            conn.commit()

    def get_recent_reflections(self, limit: int = 5) -> list[dict[str, Any]]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT content, created_at FROM reflections ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Interest helpers
    # ------------------------------------------------------------------

    def upsert_interest(self, topic: str, strength_delta: float = 1.0) -> None:
        with _lock:
            conn = self._connect()
            conn.execute(
                """
                INSERT INTO interests (topic, strength, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(topic) DO UPDATE
                    SET strength = MIN(10.0, strength + ?), updated_at = excluded.updated_at
                """,
                (topic, strength_delta, _utcnow(), strength_delta),
            )
            conn.commit()

    def get_interests(self, limit: int = 10) -> list[dict[str, Any]]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT topic, strength FROM interests ORDER BY strength DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Question helpers
    # ------------------------------------------------------------------

    def add_question(self, content: str) -> int:
        with _lock:
            conn = self._connect()
            cursor = conn.execute(
                "INSERT INTO questions (content, created_at) VALUES (?, ?)",
                (content, _utcnow()),
            )
            conn.commit()
            return cursor.lastrowid  # type: ignore[return-value]

    def resolve_question(self, question_id: int) -> None:
        with _lock:
            conn = self._connect()
            conn.execute(
                "UPDATE questions SET resolved=1, resolved_at=? WHERE id=?",
                (_utcnow(), question_id),
            )
            conn.commit()

    def get_open_questions(self) -> list[dict[str, Any]]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT id, content, created_at FROM questions WHERE resolved=0 ORDER BY id",
        ).fetchall()
        return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Heartbeat helpers
    # ------------------------------------------------------------------

    def record_heartbeat(self, status: str) -> None:
        with _lock:
            conn = self._connect()
            conn.execute(
                "INSERT INTO heartbeats (status, created_at) VALUES (?, ?)",
                (status, _utcnow()),
            )
            conn.commit()

    def get_last_heartbeat(self) -> dict[str, Any] | None:
        conn = self._connect()
        row = conn.execute(
            "SELECT status, created_at FROM heartbeats ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None
