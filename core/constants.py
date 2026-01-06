"""
Constants and default values for the Choral LLM Workbench.

This module contains all application-wide constants, default values,
and configuration parameters to ensure consistency across the codebase.
"""

from pathlib import Path
from typing import Dict, List

# Application metadata
APP_NAME = "Choral LLM Workbench"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "AI-assisted choral music composition and harmonization"

# File extensions and formats
class FileExtensions:
    MUSICXML = ".xml"
    MUSICXML_COMPRESSED = ".mxl"
    MIDI = ".mid"
    WAV = ".wav"
    MP3 = ".mp3"
    PDF = ".pdf"
    PNG = ".png"
    JSON = ".json"
    YAML = ".yaml"
    YML = ".yml"

# Audio configuration
class AudioDefaults:
    BASE_TUNING = 432.0
    TUNING_OPTIONS = [432.0, 440.0, 443.0]
    DEFAULT_SOUNDFONT = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    SAMPLE_RATE = 44100
    BIT_DEPTH = 16
    CHANNELS = 1  # Mono for choral music
    
    # Voice ranges (in MIDI note numbers)
    VOICE_RANGES = {
        "soprano": {"min": 60, "max": 84},  # C4 to C6
        "alto": {"min": 55, "max": 79},     # G3 to G5
        "tenor": {"min": 48, "max": 72},    # C3 to C5
        "bass": {"min": 40, "max": 64}      # E2 to E4
    }

# LLM configuration
class LLMDefaults:
    MAX_TOKENS = 1000
    TEMPERATURE = 0.7
    TOP_P = 0.9
    TIMEOUT = 30  # seconds
    
    # Voice-specific prompt templates
    VOICE_PROMPTS = {
        "soprano": "Create a soprano line that harmonizes with the given chords: {prompt}",
        "alto": "Create an alto line that harmonizes with the given chords: {prompt}",
        "tenor": "Create a tenor line that harmonizes with the given chords: {prompt}",
        "bass": "Create a bass line that harmonizes with the given chords: {prompt}"
    }

# UI configuration
class UIDefaults:
    THEME = "default"
    CACHE_EXAMPLES = True
    ANALYTICS_ENABLED = False
    SHOW_PROGRESS = True
    CONCURRENCY_COUNT = 1
    
    # File upload limits
    MAX_FILE_SIZE = 50  # MB
    MAX_FILES = 10

# Session configuration
class SessionDefaults:
    MAX_UNDO_STEPS = 50
    AUTO_SAVE_INTERVAL = 300  # seconds
    SESSION_TIMEOUT = 3600  # seconds

# Temporary file configuration
class TempFileDefaults:
    PREFIX = "choral_workbench_"
    SUFFIXES = {
        "musicxml": FileExtensions.MUSICXML,
        "midi": FileExtensions.MIDI,
        "wav": FileExtensions.WAV,
        "json": FileExtensions.JSON
    }
    CLEANUP_DELAY = 60  # seconds

# Logging configuration
class LoggingDefaults:
    LEVEL = "INFO"
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    BACKUP_COUNT = 5

# Validation limits
class ValidationLimits:
    MIN_TUNING = 400.0  # Hz
    MAX_TUNING = 500.0  # Hz
    MIN_TEMPO = 40      # BPM
    MAX_TEMPO = 240     # BPM
    MIN_MEASURES = 1
    MAX_MEASURES = 999
    MIN_VOICES = 1
    MAX_VOICES = 8

# Error messages (for internationalization)
class ErrorMessages:
    FILE_NOT_FOUND = "File not found: {file_path}"
    INVALID_FILE_TYPE = "Invalid file type: {file_type}. Expected: {expected_types}"
    INVALID_TUNING = "Invalid tuning frequency: {tuning} Hz. Must be between {min} and {max} Hz"
    INVALID_TEMPO = "Invalid tempo: {tempo} BPM. Must be between {min} and {max} BPM"
    SCORE_PARSING_FAILED = "Failed to parse MusicXML score: {error}"
    AUDIO_RENDERING_FAILED = "Failed to render audio: {error}"
    LLM_REQUEST_FAILED = "LLM request failed: {error}"
    SESSION_NOT_FOUND = "Session not found: {session_id}"
    INVALID_VOICE = "Invalid voice: {voice}. Must be one of: {valid_voices}"

# Success messages (for internationalization)
class SuccessMessages:
    FILE_LOADED = "File loaded successfully: {file_name}"
    AUDIO_RENDERED = "Audio rendered successfully: {file_name}"
    SCORE_SAVED = "Score saved successfully: {file_name}"
    SESSION_CREATED = "Session created: {session_id}"
    CHANGES_APPLIED = "Changes applied successfully"

# Voice information
class VoiceInfo:
    SATB_VOICES = ["soprano", "alto", "tenor", "bass"]
    VOICE_COLORS = {
        "soprano": "#FF6B6B",  # Red
        "alto": "#4ECDC4",     # Teal
        "tenor": "#45B7D1",    # Blue
        "bass": "#96CEB4"      # Green
    }
    VOICE_ABBREVIATIONS = {
        "soprano": "S",
        "alto": "A", 
        "tenor": "T",
        "bass": "B"
    }

# Path configuration
class PathDefaults:
    CONFIG_DIR = Path.home() / ".choral-workbench"
    CACHE_DIR = CONFIG_DIR / "cache"
    LOG_DIR = CONFIG_DIR / "logs"
    TEMP_DIR = Path("/tmp")
    LOCALES_DIR = Path("locales")
    EXAMPLES_DIR = Path("examples")

# HTTP/API configuration
class APIDefaults:
    TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds
    USER_AGENT = f"{APP_NAME}/{APP_VERSION}"

# Feature flags
class FeatureFlags:
    ENABLE_LLM_INTEGRATION = True
    ENABLE_AUDIO_RENDERING = True
    ENABLE_SESSION_MANAGEMENT = True
    ENABLE_GHOST_CHORDS = True
    ENABLE_COLLABORATION = False  # Future feature
    ENABLE_ADVANCED_ANALYSIS = False  # Future feature