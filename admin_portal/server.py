#!/usr/bin/env python3
"""
Anima Admin Portal — host-side process manager.

Manages Project Anima's service processes and serves the React admin UI.
Runs on the host (not in Docker) — needs direct access to host audio and processes.

Usage:
    cd admin_portal
    source .venv/Scripts/activate   # Git Bash on Windows
    python server.py

API: http://localhost:8765
UI:  http://localhost:5174 (dev) or http://localhost:8765 (production build)
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).parent.parent.resolve()
STATE_FILE  = Path(__file__).parent / "state.json"
LOG_DIR     = REPO_ROOT / "logs"
AUDIO_DIR   = REPO_ROOT / "audio_client"
DISCORD_DIR = REPO_ROOT / "discord_client"
WEBUI_DIR   = REPO_ROOT / "anima-core" / "web-ui"
DOCKER_DIR  = REPO_ROOT / "anima-core"
CLIENT_DIST = Path(__file__).parent / "client" / "dist"

LOG_DIR.mkdir(exist_ok=True)

# ── Load .env ──────────────────────────────────────────────────────────────────
_env: dict[str, str] = {}
_env_file = REPO_ROOT / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            _env[_k.strip()] = _v.strip().strip('"').strip("'")


def _e(key: str, default: str = "") -> str:
    return _env.get(key, os.environ.get(key, default))


# ── Command helpers ────────────────────────────────────────────────────────────

def _py(component_dir: Path) -> str:
    """Full path to Python inside a component's .venv."""
    return str(component_dir / ".venv" / "Scripts" / "python")


def _npm() -> str:
    return "npm.cmd" if sys.platform == "win32" else "npm"


def _tts_cmd() -> list[str]:
    cmd = [
        _py(AUDIO_DIR), str(AUDIO_DIR / "speak.py"),
        "--backend-url", _e("BACKEND_URL", "ws://localhost:8000/ws"),
        "--voice", _e("TTS_VOICE", "en-GB-RyanNeural"),
    ]
    if _e("TTS_DEVICE"):
        cmd += ["--device", _e("TTS_DEVICE")]
    return cmd


def _stt_cmd() -> list[str]:
    cmd = [
        _py(AUDIO_DIR), str(AUDIO_DIR / "capture.py"),
        "--model", _e("STT_MODEL", "base"),
    ]
    if _e("STT_DEVICE"):
        cmd += ["--device", _e("STT_DEVICE")]
    return cmd


# ── Service registry ───────────────────────────────────────────────────────────
# Add new clients here as the system grows. Each entry needs:
#   label, description, group, type ("process" | "docker")
#   For "process": cmd (callable → list[str]), cwd, log
#   For "docker": log only (compose file is fixed)
#   Optional: env_extra (callable → dict[str, str]) for process services

SERVICES: dict[str, dict] = {
    "docker": {
        "label": "Docker Stack",
        "description": "Backend · PostgreSQL · Ollama",
        "group": "infrastructure",
        "type": "docker",
        "log": LOG_DIR / "docker.log",
    },
    "webui": {
        "label": "Web UI",
        "description": "React dashboard · localhost:5173",
        "group": "infrastructure",
        "type": "process",
        "cmd": lambda: [_npm(), "run", "dev"],
        "cwd": WEBUI_DIR,
        "log": LOG_DIR / "web-ui.log",
    },
    "tts": {
        "label": "Audio Output",
        "description": "Text-to-speech · edge-tts",
        "group": "audio",
        "type": "process",
        "cmd": _tts_cmd,
        "cwd": AUDIO_DIR,
        "log": LOG_DIR / "tts.log",
    },
    "stt": {
        "label": "Audio Capture",
        "description": "Speech-to-text · faster-whisper",
        "group": "audio",
        "type": "process",
        "cmd": _stt_cmd,
        "cwd": AUDIO_DIR,
        "log": LOG_DIR / "stt.log",
    },
    "discord": {
        "label": "Discord",
        "description": "Discord channel bridge",
        "group": "channels",
        "type": "process",
        "cmd": lambda: [_py(DISCORD_DIR), str(DISCORD_DIR / "discord_client.py")],
        "cwd": DISCORD_DIR,
        "log": LOG_DIR / "discord.log",
        "env_extra": lambda: {
            "DISCORD_BOT_TOKEN": _e("DISCORD_BOT_TOKEN"),
            "DISCORD_CHANNEL_ID": _e("DISCORD_CHANNEL_ID").split("/")[-1],
        },
    },
}

# ── Process tracking ───────────────────────────────────────────────────────────

_procs: dict[str, subprocess.Popen] = {}


def _docker_running() -> bool:
    try:
        r = subprocess.run(
            ["docker", "compose", "-f", str(DOCKER_DIR / "docker-compose.yml"), "ps", "--quiet"],
            capture_output=True, text=True, timeout=5,
        )
        return bool(r.stdout.strip())
    except Exception:
        return False


def _status(sid: str) -> str:
    svc = SERVICES[sid]
    if svc["type"] == "docker":
        return "running" if _docker_running() else "stopped"
    proc = _procs.get(sid)
    if proc is None:
        return "stopped"
    if proc.poll() is None:
        return "running"
    _procs.pop(sid, None)
    return "stopped"


def _start(sid: str) -> None:
    svc = SERVICES[sid]
    log_path: Path = svc["log"]
    log_path.touch()

    if svc["type"] == "docker":
        with open(log_path, "a", encoding="utf-8") as lf:
            subprocess.Popen(
                ["docker", "compose", "-f", str(DOCKER_DIR / "docker-compose.yml"), "up", "-d"],
                stdout=lf, stderr=lf,
            )
        return

    cmd: list[str] = svc["cmd"]()
    extra: dict[str, str] = svc.get("env_extra", lambda: {})()
    env = {**os.environ, **_env, **extra}
    flags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0

    with open(log_path, "a", encoding="utf-8") as lf:
        _procs[sid] = subprocess.Popen(
            cmd, cwd=svc.get("cwd"), stdout=lf, stderr=lf,
            env=env, creationflags=flags,
        )
    log.info("Started %s (PID %d)", sid, _procs[sid].pid)


def _stop(sid: str) -> None:
    svc = SERVICES[sid]
    if svc["type"] == "docker":
        subprocess.run(
            ["docker", "compose", "-f", str(DOCKER_DIR / "docker-compose.yml"), "down"],
            capture_output=True,
        )
        return

    proc = _procs.pop(sid, None)
    if proc is None:
        return

    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
    else:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    log.info("Stopped %s", sid)


# ── State persistence ──────────────────────────────────────────────────────────

def _load_state() -> dict[str, bool]:
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            return {sid: bool(data.get(sid, False)) for sid in SERVICES}
        except Exception:
            pass
    return {sid: False for sid in SERVICES}


def _save_state(state: dict[str, bool]) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


# ── FastAPI ────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(_app: FastAPI):
    state = _load_state()
    for sid, desired in state.items():
        if desired and _status(sid) == "stopped":
            log.info("Restoring %s from persisted state", sid)
            try:
                _start(sid)
            except Exception as exc:
                log.error("Failed to restore %s: %s", sid, exc)
    yield
    for sid in list(_procs):
        try:
            _stop(sid)
        except Exception:
            pass


app = FastAPI(title="Anima Admin Portal", docs_url=None, redoc_url=None, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ServiceOut(BaseModel):
    id: str
    label: str
    description: str
    group: str
    status: str
    pid: int | None = None


@app.get("/api/services", response_model=list[ServiceOut])
def get_services() -> list[ServiceOut]:
    return [
        ServiceOut(
            id=sid,
            label=svc["label"],
            description=svc["description"],
            group=svc["group"],
            status=_status(sid),
            pid=(
                _procs[sid].pid
                if sid in _procs and _procs[sid].poll() is None
                else None
            ),
        )
        for sid, svc in SERVICES.items()
    ]


@app.post("/api/services/{sid}/start")
def start_service(sid: str) -> dict:
    if sid not in SERVICES:
        raise HTTPException(404, f"Unknown service: {sid}")
    if _status(sid) == "running":
        return {"ok": True, "already": True}
    try:
        _start(sid)
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc
    state = _load_state()
    state[sid] = True
    _save_state(state)
    return {"ok": True}


@app.post("/api/services/{sid}/stop")
def stop_service(sid: str) -> dict:
    if sid not in SERVICES:
        raise HTTPException(404, f"Unknown service: {sid}")
    _stop(sid)
    state = _load_state()
    state[sid] = False
    _save_state(state)
    return {"ok": True}


async def _tail(log_path: Path) -> AsyncGenerator[str, None]:
    log_path.touch()
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f.readlines()[-100:]:
                yield f"data: {json.dumps(line.rstrip())}\n\n"
            while True:
                line = f.readline()
                if line:
                    yield f"data: {json.dumps(line.rstrip())}\n\n"
                else:
                    await asyncio.sleep(0.25)
                    yield ": keepalive\n\n"
    except GeneratorExit:
        pass


@app.get("/api/services/{sid}/logs")
async def stream_logs(sid: str) -> StreamingResponse:
    if sid not in SERVICES:
        raise HTTPException(404)
    return StreamingResponse(
        _tail(SERVICES[sid]["log"]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )



if CLIENT_DIST.exists():
    app.mount("/", StaticFiles(directory=str(CLIENT_DIST), html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8765, log_level="info", reload=False)
