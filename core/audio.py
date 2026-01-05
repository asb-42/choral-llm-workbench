# core/audio.py

import subprocess
from pathlib import Path
from core.config import Config

config = Config()  # globale Konfiguration laden

def midi_to_wav(midi_file: str, wav_file: str, tuning: float = None, soundfont_path: str = None):
    """
    Rendert eine MIDI-Datei in WAV mit FluidSynth.
    Args:
        midi_file: Pfad zur MIDI-Datei
        wav_file: Pfad zur Ausgabedatei WAV
        tuning: Basisstimmung in Hz (z. B. 432, 440, 443). Wenn None, wird Default aus Config genommen.
        soundfont_path: Pfad zur SoundFont-Datei (SF2)
    """
    midi_file = Path(midi_file)
    wav_file = Path(wav_file)

    if tuning is None:
        tuning = config.audio_tuning_default

    if soundfont_path is None:
        # Standardpfad für SF2, kann in Config erweitert werden
        soundfont_path = Path.home() / ".fluidsynth" / "default_sound_font.sf2"

    if not soundfont_path.exists():
        raise FileNotFoundError(f"SoundFont not found: {soundfont_path}")

    # FluidSynth-Befehl
    cmd = [
        "fluidsynth",
        "-F", str(wav_file),
        "-T", "wav",
        str(soundfont_path),
        str(midi_file)
    ]

    print(f"Rendering WAV at {tuning}Hz...")
    try:
        # FluidSynth kann Base-Tuning nur über -g/-o Optionen oder eigene SF2-Einstellungen steuern
        # Viele Distributionen unterstützen direkt keine -t Option
        subprocess.run(cmd, check=True)
        print(f"Rendered WAV: {wav_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during MIDI->WAV rendering: {e}")
        raise
