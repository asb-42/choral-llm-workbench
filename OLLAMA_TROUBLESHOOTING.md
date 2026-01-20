# Ollama Connection Troubleshooting Guide

## Issue: Connection refused to remote Ollama server

### Problem Analysis
- Local Ollama (127.0.0.1:11434): ✅ Working
- Remote Ollama (192.168.178.200:11434): ❌ Connection refused
- Port 11434 on remote server is **closed** (nmap shows "closed")

### Root Cause
The remote Ollama server is not configured to accept external connections.

### Solutions for Remote Server (192.168.178.200)

#### Option 1: Allow External Connections (Recommended)
```bash
# Stop current Ollama
pkill ollama

# Start Ollama with external binding
export OLLAMA_HOST=0.0.0.0
ollama serve

# Or permanently in environment
echo 'export OLLAMA_HOST=0.0.0.0' >> ~/.bashrc
source ~/.bashrc
ollama serve
```

#### Option 2: Configure Systemd Service (for permanent setup)
```bash
# Create/edit systemd service
sudo nano /etc/systemd/system/ollama.service

# Content:
[Unit]
Description=Ollama Server
After=network.target

[Service]
Type=simple
User=asb
Environment="OLLAMA_HOST=0.0.0.0"
ExecStart=/usr/bin/ollama serve
Restart=always

[Install]
WantedBy=multi-user.target

# Reload and start
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama
```

#### Option 3: Use SSH Tunnel (if direct connection not desired)
```bash
# On client machine, create tunnel
ssh -L 11434:localhost:11434 asb@192.168.178.200

# Then connect to localhost:11434 in the UI
```

### Verification
After fixing, verify with:
```bash
# From client machine
nmap -p 11434 192.168.178.200
# Should show: 11434/tcp open http

# Test API connection
curl http://192.168.178.200:11434/api/tags
# Should return JSON with models
```

### Current Status
- ✅ Code implementation complete
- ✅ UI shows connection errors clearly
- ❌ Remote server needs configuration
- ⚠️ User needs to configure Ollama to accept external connections