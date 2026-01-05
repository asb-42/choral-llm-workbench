# Datei: core/audio/audio.py

import tempfile
import os
from music21 import midi
import subprocess

DEFAULT_SF2 = os.path.expanduser("~/.fluidsynth/default_sound_font.sf2")

def score_to_midi(score, output_path=None):
    """Speichert einen Music21 Score als MIDI-Datei"""
    if output_path is None:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mid")
        output_path = tmp_file.name
    mf = midi.translate.music21ObjectToMidiFile(score)
    mf.open(output_path, 'wb')
    mf.write()
    mf.close()
    return output_path

def midi_to_wav(midi_path, sf2_path=None, output_wav=None):
    """Konvertiert eine MIDI-Datei in WAV mittels FluidSynth"""
    if sf2_path is None:
        sf2_path = DEFAULT_SF2
    if output_wav is None:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        output_wav = tmp_file.name
    command = ["fluidsynth", "-ni", sf2_path, midi_path, "-F", output_wav, "-r", "44100"]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Fehler beim Rendern von WAV: {e.stderr.decode()}")
    return output_wav
