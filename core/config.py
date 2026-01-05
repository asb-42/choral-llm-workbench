"""
Global configuration for Choral LLM Workbench.
"""

from enum import Enum

class TuningFrequency(Enum):
    HZ_432 = 432
    HZ_440 = 440
    HZ_443 = 443

# Default base tuning
BASE_TUNING = TuningFrequency.HZ_432

AUDIO_BASE_TUNING_HZ = 432  # Default base tuning in Hz
SUPPORTED_TUNINGS = [432, 440, 443]

# Weitere globale Einstellungen können hier hinzugefügt werden
# z.B. default MIDI instrument, default SoundFont-Pfad etc.
DEFAULT_SOUNDFONT_PATH = "~/.fluidsynth/default_sound_font.sf2"
