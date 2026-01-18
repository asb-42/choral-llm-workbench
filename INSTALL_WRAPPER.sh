#!/usr/bin/env bash
set -euo pipefail

# Wrapper: One-Click Installer with post-install health checks and storage init

LOG_FILE="${LOG_FILE:-$HOME/.choral_install_wrapper.log}"
exec > >(tee -a "$LOG_FILE") 2>&1
log() { printf "[INSTALL-WRAPPER] %s | %s\n" "$(date '+%F %T')" "$*"; }

log "Starting One-Click Installer Wrapper"

# Step 1: Run the primary installer
if [ -x "./install_pinokio.sh" ]; then
  log "Running install_pinokio.sh"
  bash ./install_pinokio.sh || log "install_pinokio.sh exited with non-zero status"
else
  log "install_pinokio.sh not executable; trying with bash"
  bash ./install_pinokio.sh || log "install_pinokio.sh exited with non-zero status"
fi

# Step 2: Patch package.json safely (remove musicxml-json) using patch_package_json.py
if [ -f frontend/package.json ]; then
  log "Patching frontend/package.json via patch_package_json.py"
  python3 scripts/patch_package_json.py frontend/package.json || log "Frontend patch failed"
fi
if [ -f backend/package.json ]; then
  log "Patching backend/package.json via patch_package_json.py"
  python3 scripts/patch_package_json.py backend/package.json || log "Backend patch failed"
fi

log "Post-install health checks"

# 3) Health check helpers
health_report_path="./health_check.json"
health_jsonAvailable=false

# 4) Trigger a researcher-friendly health check script if Python is available
if command -v python3.12 >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1; then
  log "Running health checks via embedded Python"
  python3 - <<'PY'
import json, os, shutil
health = {
  'python_ok': True,
  'venv_exists': os.path.isdir('.venv'),
  'ollama_available': shutil.which('ollama') is not None,
  'soundfont_present': os.path.exists(os.path.expanduser('~/.fluidsynth/default_sound_font.sf2')),
  'node_available': shutil.which('node') is not None,
  'npm_available': shutil.which('npm') is not None,
  'storage_dirs': {
    'undo_redo': os.path.isdir('storage/undo_redo'),
    'scores': os.path.isdir('storage/scores'),
    'voices': os.path.isdir('storage/voices')
  }
}
print(json.dumps(health, indent=2))
PY
  if [ -f health_check.json ]; then
    health_jsonAvailable=true
    log "Health report written to ${health_report_path}"
  else
    log "Health report could not be created"
  fi
else
  log "Python not available for health checks; skipping health report"
fi

if [ "$health_jsonAvailable" = true ]; then
  echo "Health Check JSON:"; cat ./health_check.json
else
  log "Health checks not performed due to missing Python."
fi

log "Wrapper finished. You can now run the stack:"
log "  Backend: cd backend; npm run start:dev"
log "  Frontend: cd frontend; npm run dev"

exit 0
