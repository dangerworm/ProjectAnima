"""Dependency-injection container.

A single ``AnimaContainer`` owns all long-lived objects and is created once
at startup.  Callers import it and use its attributes rather than
instantiating subsystems directly.
"""

from __future__ import annotations

from pathlib import Path

from anima.core.being import IdentityManager
from anima.core.conversation import ConversationManager
from anima.core.heartbeat import Heartbeat
from anima.core.memory import MemoryManager
from anima.core.reflection import ReflectionEngine
from anima.llm.client import LLMClient
from anima.settings import Settings
from anima.storage.database import Database


class AnimaContainer:
    """Wires together all subsystems."""

    def __init__(self, settings: Settings | None = None) -> None:
        cfg = settings or Settings()

        db_path = Path(cfg.data_dir) / "anima.db"
        self.db = Database(db_path)

        self.llm = LLMClient(
            api_key=cfg.llm_api_key,
            base_url=cfg.llm_base_url,
            model=cfg.llm_model,
        )

        self.identity = IdentityManager(self.db)
        self.memory = MemoryManager(self.db)
        self.reflection = ReflectionEngine(self.llm, self.memory)

        self.conversation = ConversationManager(
            db=self.db,
            identity_manager=self.identity,
            memory_manager=self.memory,
            llm=self.llm,
            reflection_engine=self.reflection,
        )

        self.heartbeat = Heartbeat(self.db, interval=cfg.heartbeat_interval)
