#!/usr/bin/env bash
set -euo pipefail

# Simplified, robust health check for the installer flow.
health_json="./health_check.json"

python_present=0
if command -v python3.12 >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1; then
  python_present=1
fi
python_ok=$([ "$python_present" -eq 1 ] && echo true || echo false)

venv_exists=$([ -d ".venv" ] && echo true || echo false)

ollama_available=$([ -x "$(command -v ollama 2>/dev/null)" ] && echo true || echo false)

soundfont_present=$([ -f "$HOME/.fluidsynth/default_sound_font.sf2" ] && echo true || echo false)

node_available=$([ -x "$(command -v node 2>/dev/null)" ] && echo true || echo false)
npm_available=$([ -x "$(command -v npm 2>/dev/null)" ] && echo true || echo false)

storage_undo_redo=$([ -d storage/undo_redo ] && echo true || echo false)
storage_scores=$([ -d storage/scores ] && echo true || echo false)
storage_voices=$([ -d storage/voices ] && echo true || echo false)

cat > "$health_json" << JSON
{
  "python_ok": $python_ok,
  "venv_exists": $venv_exists,
  "ollama_available": $ollama_available,
  "soundfont_present": $soundfont_present,
  "node_available": $node_available,
  "npm_available": $npm_available,
  "storage_dirs": {
    "undo_redo": $storage_undo_redo,
    "scores": $storage_scores,
    "voices": $storage_voices
  }
}
JSON

echo "Health report written to $health_json"
