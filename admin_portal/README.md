# admin_portal

Local admin portal for Project Anima. Starts, stops, and monitors all Anima services from
a browser UI. Persists desired service state across restarts.

Runs entirely on the host — it manages host-level processes (audio clients, Discord) and
the Docker stack. It is completely separate from Anima itself.

- **API / production UI**: `http://localhost:8765`
- **Dev UI**: `http://localhost:5174`

## Services managed

| Service | What it runs |
|---------|-------------|
| Docker Stack | `docker compose up/down` in `anima-core/` |
| Web UI | `npm run dev` in `anima-core/web-ui/` |
| Audio Output | `audio_client/speak.py` (TTS) |
| Audio Capture | `audio_client/capture.py` (STT) |
| Discord | `discord_client/discord_client.py` |

Service state is persisted to `state.json`. On server restart, any service that was running
will be relaunched automatically.

## Setup

### 1. Python backend

```bash
cd admin_portal
python -m venv .venv
source .venv/Scripts/activate   # Git Bash on Windows
python -m pip install -r requirements.txt
```

### 2. React frontend

```bash
cd admin_portal/client
npm install
```

## Running

### Development (frontend + backend separately)

Terminal 1 — backend:
```bash
cd admin_portal
source .venv/Scripts/activate
python server.py
```

Terminal 2 — frontend dev server:
```bash
cd admin_portal/client
npm run dev
```

Open `http://localhost:5174`.

### Production (frontend served by backend)

```bash
cd admin_portal/client
npm run build

cd ..
source .venv/Scripts/activate
python server.py
```

Open `http://localhost:8765`.

## Extending

To add a new client or service, add an entry to the `SERVICES` dict in `server.py` and
the `ServiceId` / `ServiceGroup` types in `client/src/types.ts`. No other changes needed.

## Logs

All service logs are written to `logs/` in the repo root (same as `start.sh`). The log
panel in the UI streams them live.
