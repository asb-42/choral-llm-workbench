# core/audio.py

import subprocess
import os
import tempfile
from mido import MidiFile

DEFAULT_SOUNDFONT_PATH = os.path.expanduser("~/.fluidsynth/default_sound_font.sf2")

def midi_to_wav(midi_path: str, wav_path: str, soundfont_path: str = DEFAULT_SOUNDFONT_PATH, base_tuning: float = 432.0):
    """
    Render a MIDI file to WAV using FluidSynth.

    Parameters:
    - midi_path: path to the input MIDI file
    - wav_path: path to the output WAV file
    - soundfont_path: path to the SoundFont (.sf2)
    - base_tuning: base tuning frequency in Hz (default 432.0)
    """
    if not os.path.exists(midi_path):
        raise FileNotFoundError(f"MIDI file not found: {midi_path}")

    if not os.path.exists(soundfont_path):
        raise FileNotFoundError(
            f"SoundFont file not found: {soundfont_path}\n"
            f"Please download a GM SoundFont (e.g., FluidR3_GM.sf2) into {os.path.dirname(soundfont_path)}"
        )

    print(f"Rendering WAV at {base_tuning}Hz using SoundFont: {soundfont_path}...")

    # Build FluidSynth command
    # Use -F for output WAV, set midi input, and tuning if supported
    cmd = [
        "fluidsynth",
        "-F", wav_path,
        "-T", "wav",
        "-a", "alsa" if os.name != "nt" else "coreaudio",
        "-o", f"synth.tuning={base_tuning}",
        soundfont_path,
        midi_path
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during MIDI->WAV rendering: {e}\nOutput:\n{e.output.decode()}\nStderr:\n{e.stderr.decode()}")
        raise

    print(f"Rendered WAV: {wav_path}")
    return wav_path
