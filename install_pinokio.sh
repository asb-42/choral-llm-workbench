#!/usr/bin/env bash
set -euo pipefail

# Robust Pinokio-style installer with defensive checks and graceful fallbacks
# - Non-interactive, robust installation for Python env, Node deps, SoundFont, and optional Ollama

LOG_FILE="${LOG_FILE:-$HOME/.choral_install.log}"
exec > >(tee -a "$LOG_FILE") 2>&1
log() { local t; t=$(date +"%Y-%m-%d %H:%M:%S"); echo "[INSTALL] $t | $*"; }
exists() { command -v "$1" >/dev/null 2>&1; }
remote_fail() { log "ERROR: $1"; }

log "Starting robust Pinokio installer"

# 1) System detection
if exists apt-get; then
  PKGMGR="apt-get"
  UPDATE="apt-get update"
  INSTALL="apt-get install -y"
elif exists brew; then
  PKGMGR="brew"
  UPDATE="brew update"
  INSTALL="brew install"
else
  log "Unsupported OS. This installer currently targets Debian/Ubuntu or macOS with Homebrew."
  log "Proceeding with a best-effort installation; some steps may be skipped."
  PKGMGR="none"
fi

# 2) Python 3.12
log "Checking for Python 3.12"
if command -v python3.12 >/dev/null 2>&1; then
  log "Python 3.12 is present"
else
  if [ "$PKGMGR" = "apt-get" ]; then
    log "Installing Python 3.12 via apt-get"
    sudo apt-get update || true
    sudo apt-get install -y python3.12 python3.12-venv python3.12-dev python3-pip git || {
      log "Warning: Failed to install Python 3.12 via apt; continuing to best effort"
    }
  elif [ "$PKGMGR" = "brew" ]; then
    log "Installing Python 3.12 via brew"
    brew install python@3.12 || log "Warning: brew install python@3.12 failed"
  else
    log "Manual action required: Install Python 3.12 and rerun the installer."
  fi
fi

# Re-check
if ! command -v python3.12 >/dev/null 2>&1; then
  log "ERROR: Python 3.12 not found. Aborting installer."
  exit 1
fi

# 3) Virtual environment
ROOT_DIR=$(pwd)
VENVDIR="$ROOT_DIR/.venv"
if [ -d "$VENVDIR" ]; then
  log "Using existing virtual environment at $VENVDIR"
else
  log "Creating Python virtual environment at $VENVDIR"
  python3.12 -m venv "$VENVDIR" || { log "Failed to create virtual environment"; exit 1; }
fi
source "$VENVDIR/bin/activate" || { log "Failed to activate virtual environment"; exit 1; }
log "Virtual environment activated"

# 4) Python dependencies
if [ -f requirements.txt ]; then
  log "Installing Python dependencies from requirements.txt"
  if ! pip install -U pip; then log "Warning: pip upgrade failed"; fi
  if ! pip install -r requirements.txt; then log "Warning: Somepython dependencies failed to install"; fi
else
  log "requirements.txt not found; skipping Python dependencies install"
fi

# 5) SoundFont
mkdir -p ~/.fluidsynth
if [ -f ~/.fluidsynth/default_sound_font.sf2 ]; then
  log "SoundFont already present at ~/.fluidsynth/default_sound_font.sf2"
else
  log "Attempting to download default SoundFont"
  if command -v curl >/dev/null 2>&1; then
    if curl -L -o ~/.fluidsynth/default_sound_font.sf2 https://member.keymusician.com/Member/FluidR3_GM/FluidR3_GM.sf2; then
      log "SoundFont downloaded"
    else
      log "Warning: SoundFont download failed"
    fi
  elif command -v wget >/dev/null 2>&1; then
    if wget -O ~/.fluidsynth/default_sound_font.sf2 https://member.keymusician.com/Member/FluidR3_GM/FluidR3_GM.sf2; then
      log "SoundFont downloaded"
    else
      log "Warning: SoundFont download failed"
    fi
  else
    log "No downloader (curl/wget) available; skipping SoundFont download"
  fi
fi

# 6) Ollama
if command -v ollama >/dev/null 2>&1; then
  log "Ollama found on PATH"
else
  log "WARNING: Ollama not found. Local LLM integration will require installation in Phase 7+ (or later)."
fi

# 7) Node dependencies (optional but encouraged)
if [ -d frontend ]; then
  log "Installing frontend dependencies (npm ci)"
  (cd frontend && npm ci) && log "Frontend dependencies installed" || log "Warning: Frontend npm install failed"
fi
if [ -d backend ]; then
  log "Installing backend dependencies (npm ci)"
  (cd backend && npm ci) && log "Backend dependencies installed" || log "Warning: Backend npm install failed"
fi

log "Installation complete. Summary:" 
log "- Python venv: $VENVDIR"
log "- SoundFont: ${HOME}/.fluidsynth/default_sound_font.sf2 (attempted)"
log "- Ollama: ${command -v ollama >/dev/null 2>&1 && echo 'present' || echo 'not found'}"
log "- UI: Frontend and Backend install attempted (npm)"

if [ -n "$LOG_FILE" ]; then
  log "Logs written to $LOG_FILE"
fi
