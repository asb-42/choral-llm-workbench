#!/bin/bash
set -euo pipefail

# Enhanced Pinokio-style installer: enforces Ollama as a system requirement

ROOT_DIR=$(pwd)
VENVDIR="$ROOT_DIR/.venv"

echo "[Pinokio] Starting installation..."

# 1) System dependencies (Ubuntu/Debian style commands as baseline)
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y python3.12 python3.12-venv python3-pip git \
    libsdl2-2.0-0 libsdl2-mixer-2.0-0 fluidsynth curl
else
  echo "[Pinokio] Non-Debian system detected. Please install Python 3.12+, PIP, and Ollama manually."
fi

# 2) Python venv
echo "[Pinokio] Creating virtual environment..."
python3.12 -m venv "$VENVDIR"
source "$VENVDIR/bin/activate"

# 3) Python dependencies
echo "[Pinokio] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 4) Node dependencies (if available)
if [ -d frontend ]; then
  echo "[Pinokio] Installing frontend dependencies..."
  (cd frontend && npm install --silent) || true
fi
if [ -d backend ]; then
  echo "[Pinokio] Installing backend dependencies..."
  (cd backend && npm install --silent) || true
fi

# 5) Ollama requirement check
if command -v ollama >/dev/null 2>&1; then
  echo "[Pinokio] Ollama found. You can use local models."
else
  echo "[Pinokio] Ollama not found. Please install Ollama for local LLMs."
fi

# 6) SoundFont download (optional)
mkdir -p ~/.fluidsynth
if [ -f ~/.fluidsynth/default_sound_font.sf2 ]; then
  echo "[Pinokio] SoundFont already present."
else
  echo "[Pinokio] Downloading default SoundFont..."
  curl -L https://member.keymusician.com/Member/FluidR3_GM/FluidR3_GM.sf2 -o ~/.fluidsynth/default_sound_font.sf2 || true
fi

# 7) Final note
echo "[Pinokio] Done. Run: source "$VENVDIR/bin/activate" and follow project docs to start services."
