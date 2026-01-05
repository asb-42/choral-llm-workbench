import subprocess
import tempfile
from mido import MidiFile, MidiTrack, Message
from copy import deepcopy

def adjust_midi_for_tuning(midi_path, base_tuning=432.0):
    """
    Adjust all note pitches in the MIDI file according to the base tuning.
    Returns a path to a temporary adjusted MIDI file.
    """
    # Load original MIDI
    mid = MidiFile(midi_path)
    factor = base_tuning / 440.0  # relative to standard 440 Hz

    # Create a new MIDI object to avoid modifying the original
    new_mid = MidiFile()
    for track in mid.tracks:
        new_track = MidiTrack()
        for msg in track:
            if msg.type == 'note_on' or msg.type == 'note_off':
                new_note = int(msg.note * factor)
                new_msg = deepcopy(msg)
                new_msg.note = max(0, min(127, new_note))
                new_track.append(new_msg)
            else:
                new_track.append(deepcopy(msg))
        new_mid.tracks.append(new_track)

    # Save to temporary file
    tmp_midi = tempfile.NamedTemporaryFile(delete=False, suffix=".mid")
    new_mid.save(tmp_midi.name)
    return tmp_midi.name

def render_audio_with_tuning(*, midi_path, wav_path, base_tuning=432.0, soundfont_path=None):
    """
    Render a MIDI file to WAV using FluidSynth with manual pitch adjustment for base tuning.
    All arguments are keyword-only to avoid parameter conflicts.
    """
    # Adjust MIDI for base tuning
    try:
        adjusted_midi = adjust_midi_for_tuning(midi_path, base_tuning=base_tuning)
        print(f"Adjusting MIDI pitches for base tuning {base_tuning} Hz...")
    except Exception as e:
        print(f"Error adjusting MIDI for tuning: {e}")
        adjusted_midi = midi_path  # fallback to original MIDI

    if soundfont_path is None:
        soundfont_path = "/home/asb/.fluidsynth/default_sound_font.sf2"

    print(f"Rendering WAV at {base_tuning} Hz using SoundFont {soundfont_path} ...")
    cmd = [
        "fluidsynth",
        "-F", wav_path,
        "-T", "wav",
        soundfont_path,
        adjusted_midi
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"WAV rendered at {base_tuning} Hz: {wav_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during MIDI->WAV rendering: {e}")
