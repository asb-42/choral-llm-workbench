"""
Configuration file for Choral LLM Workbench
Stores user preferences (not committed to git)
"""

import json
import os

CONFIG_FILE = "user_config.json"


def load_config():
    """Load user configuration from file"""
    default_config = {
        "ollama_host": "localhost",
        "ollama_port": "11434"
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                loaded = json.load(f)
                default_config.update(loaded)
        except Exception as e:
            print(f"Warning: Could not load config file, using defaults: {e}")
    
    return default_config


def save_config(config):
    """Save user configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"DEBUG: Saved config: {config}")
    except Exception as e:
        print(f"Error saving config file: {e}")


def get_ollama_host():
    """Get Ollama host from config"""
    config = load_config()
    host = config.get("ollama_host", "localhost")
    print(f"DEBUG: get_ollama_host() returning: {host}")
    return host


def get_ollama_port():
    """Get Ollama port from config"""
    config = load_config()
    port = config.get("ollama_port", "11434")
    print(f"DEBUG: get_ollama_port() returning: {port}")
    return port


def set_ollama_host(host, port=None):
    """Set Ollama host in config"""
    config = load_config()
    config["ollama_host"] = host
    if port:
        config["ollama_port"] = port
    save_config(config)


def get_ollama_base_url():
    """Get full Ollama base URL from config"""
    host = get_ollama_host()
    port = get_ollama_port()
    url = f"http://{host}:{port}"
    print(f"DEBUG: get_ollama_base_url() returning: {url}")
    return url