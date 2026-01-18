#!/usr/bin/env bash
set -euo pipefail

# Robust Pinokio-style installer with defensive checks and graceful fallbacks

LOG_FILE="${LOG_FILE:-$HOME/.choral_install.log}"
exec > >(tee -a "$LOG_FILE") 2>&1
log() { printf "[INSTALL] %s | %s\n" "$(date '+%F %T')" "$*"; }
exists() { command -v "$1" >/dev/null 2>&1; }

log "Starting robust Pinokio installer"

# 0) Pre-flight compatibility patches (JSON/text-based) to reduce later failures
log "Applying pre-flight compatibility patches (if needed)"
if [ -f requirements.txt ]; then
  if grep -q "pyfluidsynth>=2.3" requirements.txt; then
    sed -i 's/pyfluidsynth>=2.3/pyfluidsynth>=1.3.4/' requirements.txt
    log "Patched pyfluidsynth to >=1.3.4 in requirements.txt"
  fi
  if grep -q "fluidsynth>=0.3" requirements.txt; then
    sed -i 's/fluidsynth>=0.3/fluidsynth>=0.2.0/' requirements.txt
    log "Patched fluidsynth to >=0.2.0 in requirements.txt"
  fi
fi

# 1) System detection
if command -v apt-get >/dev/null 2>&1; then
  PKGMGR="apt-get"
  UPDATE="apt-get update"
  INSTALL="apt-get install -y"
elif command -v brew >/dev/null 2>&1; then
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
  if ! pip install -r requirements.txt; then
    log "Initial Python dependencies install failed. Attempting fallback (explicit pyfluidsynth==1.3.4)"
    if grep -q "pyfluidsynth" requirements.txt; then
      sed -i 's/pyfluidsynth.*/pyfluidsynth==1.3.4/' requirements.txt
      if ! pip install -r requirements.txt; then
        log "Warning: pyfluidsynth fallback install failed. Continuing without it."
      else
        log "Pyfluidsynth fallback installed successfully."
      fi
    else
      log "No pyfluidsynth entry found; continuing"
    fi
  fi
else
  log "requirements.txt not found; skipping Python dependencies install"
fi

# 5) Patch package.json safely (remove musicxml-json) using a tiny Python script instead of here-doc
cat > /tmp/patch_json.py << 'PY'
import json,sys
p = sys.argv[1]
try:
  with open(p, 'r', encoding='utf-8') as f:
    data = json.load(f)
except Exception:
  sys.exit(0)
if isinstance(data, dict) and data.get('dependencies') and isinstance(data['dependencies'], dict):
  if 'musicxml-json' in data['dependencies']:
    del data['dependencies']['musicxml-json']
    with open(p, 'w', encoding='utf-8') as f:
      json.dump(data, f, indent=2)
    print(f"Patched {p}")
else:
  print(f"No patch needed for {p}")
PY
for proj in frontend backend; do
  if [ -f "$proj/package.json" ]; then
    log "Patching $proj/package.json to remove musicxml-json (JSON-safe) via patch_json.py"
    python3 /tmp/patch_json.py "$proj/package.json" || log "Patch script failed for $proj/package.json"
  fi
done
rm -f /tmp/patch_json.py

# 6) Node dependencies (optional but encouraged)
for proj in frontend backend; do
  if [ -d "$proj" ]; then
    if [ -f "$proj/package-lock.json" ]; then
      log "Installing $proj dependencies via npm ci"
      (cd $proj && npm ci) && log "$proj dependencies installed" || log "Warning: npm ci failed; attempting npm install"
      (cd $proj && npm install) || true
    elif [ -f "$proj/package.json" ]; then
      log "Installing $proj dependencies via npm install"
      (cd $proj && npm install) || log "Frontend/backend npm install failed"
    else
      log "$proj has no package.json; skipping npm install"
    fi
  fi
done

# 7) Ollama presence check
if command -v ollama >/dev/null 2>&1; then
  log "Ollama found on PATH"
else
  log "WARNING: Ollama not found. Local LLM integration will require installation in Phase 7+ (or later)."
fi

# 8) SoundFont
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

log "Installation complete. Summary above."
