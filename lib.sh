#!/usr/bin/env bash
# ============================================================
#  Project Anima — shared shell helpers
#  Sourced by start.sh and stop.sh. Not executable on its own.
# ============================================================

# ── Colours / logging ───────────────────────────────────────
GRN="\033[0;32m"; YLW="\033[0;33m"; RED="\033[0;31m"; RST="\033[0m"
ok()  { echo -e "${GRN}✓ $*${RST}"; }
inf() { echo -e "${YLW}→ $*${RST}"; }
err() { echo -e "${RED}✗ $*${RST}"; }

# ── Process management (Windows / Git Bash) ─────────────────
# MSYS_NO_PATHCONV=1 stops Git Bash rewriting /F /T /PID into Windows paths.

# kill_tree <pid> [label]
#   Kill a PID and all its descendants. Returns 0 on success.
kill_tree() {
    local pid="$1"
    local label="${2:-}"
    [[ -z "$pid" ]] && return 1
    if MSYS_NO_PATHCONV=1 taskkill /F /T /PID "$pid" >/dev/null 2>&1; then
        [[ -n "$label" ]] && ok "$label stopped (PID $pid)"
        return 0
    fi
    return 1
}

# kill_by_cmdline <pattern> [label]
#   Kill every process whose full command line matches *<pattern>*.
#   Needed because `speak.py`, `capture.py`, `vite` etc. aren't process
#   names — they're arguments to python.exe / node.exe, so /IM can't see them.
kill_by_cmdline() {
    local pattern="$1"
    local label="${2:-}"
    local pids
    pids=$(powershell -NoProfile -Command \
        "Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -like '*$pattern*' } | Select-Object -ExpandProperty ProcessId" \
        2>/dev/null | tr -d '\r' | grep -v '^[[:space:]]*$' || true)
    [[ -z "$pids" ]] && return 1
    local count=0
    for pid in $pids; do
        if MSYS_NO_PATHCONV=1 taskkill /F /T /PID "$pid" >/dev/null 2>&1; then
            count=$((count+1))
        fi
    done
    if (( count > 0 )) && [[ -n "$label" ]]; then
        ok "$label stopped ($count process(es))"
    fi
    (( count > 0 ))
}
