# File: core/audio.py

import subprocess
import tempfile
from pathlib import Path
from mido import MidiFile, MidiTrack, Message
from copy import deepcopy
import math

from core.config import Config  # Base-Tuning aus globaler Config

config = Config()

def midi_to_wav(midi_path: str, wav_path: str, base_tuning: float = None, soundfont_path: str = None):
    """
    Render a MIDI file to WAV using FluidSynth, adjusting base tuning if requested.
    - midi_path: path to input MIDI file
    - wav_path: path to output WAV file
    - base_tuning: target A4 frequency (Hz), e.g., 432, 440, 443
    - soundfont_path: path to .sf2 soundfont file
    """
    midi_path = str(Path(midi_path).resolve())
    wav_path = str(Path(wav_path).resolve())
    
    if soundfont_path is None:
        soundfont_path = str(Path.home() / ".fluidsynth" / "default_sound_font.sf2")
    soundfont_path = str(Path(soundfont_path).resolve())
    
    # Wenn base_tuning angegeben ist, MIDI umtransponieren
    if base_tuning is None:
        base_tuning = config.base_tuning  # Standard aus Config
    
    if abs(base_tuning - 440.0) > 0.01:
        # Berechne Halbton-Offset für MIDI
        semitone_offset = 12 * math.log2(base_tuning / 440.0)
        print(f"Transposing MIDI by {semitone_offset:.3f} semitones for base tuning {base_tuning} Hz")
        
        # MIDI einlesen und transponieren
        midi = MidiFile(midi_path)
        transposed_midi = deepcopy(midi)
        for track in transposed_midi.tracks:
            for msg in track:
                if msg.type in ('note_on', 'note_off'):
                    msg.note = int(round(msg.note + semitone_offset))
        # temporäre MIDI-Datei schreiben
        tmp_midi_file = Path(tempfile.mktemp(suffix=".mid"))
        transposed_midi.save(tmp_midi_file)
        midi_path_to_use = str(tmp_midi_file)
    else:
        midi_path_to_use = midi_path
    
    # FluidSynth aufrufen (ohne -o synth.tuning)
    cmd = [
        "fluidsynth",
        "-F", wav_path,
        "-T", "wav",
        soundfont_path,
        midi_path_to_use
    ]
    print(f"Rendering WAV at {base_tuning} Hz...")
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"Rendered WAV: {wav_path}")
    except subprocess.CalledProcessError as e:
        print("Error during MIDI->WAV rendering:", e)
        print("stdout:", e.stdout.decode())
        print("stderr:", e.stderr.decode())
        raise e
    finally:
        # temporäre MIDI-Datei löschen
        if base_tuning != 440.0:
            tmp_midi_file.unlink(missing_ok=True)

def generate_test_midi(path: str):
    """Erzeugt ein kurzes Test-MIDI mit C-Dur Akkord"""
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Ein einfacher Akkord: C4, E4, G4
    notes = [60, 64, 67]
    for n in notes:
        track.append(Message('note_on', note=n, velocity=64, time=0))
    for n in notes:
        track.append(Message('note_off', note=n, velocity=64, time=480))
    
    mid.save(path)
    print(f"MIDI file generated: {path}")
