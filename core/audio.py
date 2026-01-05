# core/audio.py

import os
import tempfile
import subprocess
from mido import MidiFile, MidiTrack, Message
from core.config import Config

config = Config()  # Zugriff auf globales Base-Tuning

def midi_to_wav(midi_path: str, wav_path: str, soundfont_path: str = None, base_tuning: float = None):
    """
    Convert a MIDI file to WAV using FluidSynth.
    If base_tuning is provided, adjust MIDI pitches accordingly.
    """
    if base_tuning is None:
        base_tuning = config.base_tuning  # Standardwert aus Konfig

    if soundfont_path is None:
        # Default SoundFont
        soundfont_path = os.path.expanduser("~/.fluidsynth/default_sound_font.sf2")

    # Laden MIDI und ggf. Pitch anpassen
    midi = MidiFile(midi_path)
    if base_tuning != 440.0:
        print(f"Adjusting MIDI pitches for base tuning {base_tuning} Hz...")
        ratio = base_tuning / 440.0
        for track in midi.tracks:
            for msg in track:
                if msg.type in ['note_on', 'note_off']:
                    original = msg.note
                    new_note = int(round(original * ratio))
                    msg.note = max(0, min(127, new_note))  # MIDI-Note clampen

        # Speichere temporäres MIDI mit korrigierten Noten
        temp_midi_fd, temp_midi_path = tempfile.mkstemp(suffix=".mid")
        os.close(temp_midi_fd)
        midi.save(temp_midi_path)
        midi_path = temp_midi_path

    print(f"Rendering WAV at {base_tuning} Hz using SoundFont {soundfont_path} ...")
    try:
        subprocess.run(
            [
                "fluidsynth",
                "-F", wav_path,
                "-T", "wav",
                soundfont_path,
                midi_path
            ],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error during MIDI->WAV rendering: {e}")
        raise e
    finally:
        # Temporäre MIDI-Datei löschen, falls erstellt
        if base_tuning != 440.0:
            os.remove(midi_path)

    print(f"WAV file generated: {wav_path}")
