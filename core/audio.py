import subprocess
import tempfile
from mido import MidiFile, MidiTrack, Message
from copy import deepcopy
from pathlib import Path
from core.config import get_config

try:
    from music21 import converter, stream
except ImportError:
    converter = None
    stream = None


def adjust_midi_for_tuning(midi_path, base_tuning=432.0):
    """
    Adjust all note pitches in MIDI file according to base tuning.
    Returns a path to a temporary adjusted MIDI file.
    """
    # Load original MIDI
    mid = MidiFile(midi_path)
    factor = base_tuning / 440.0  # relative to standard 440 Hz

    # Create a new MIDI object to avoid modifying original
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


def score_to_midi(score, output_path=None):
    """
    Convert a Music21 Score to MIDI file with proper part offsets.
    
    Args:
        score: Music21 Score object
        output_path: Output MIDI file path (optional)
        
    Returns:
        Path to MIDI file
    """
    if converter is None:
        raise ImportError("music21 is required for score_to_midi")
    
    if output_path is None:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mid")
        output_path = tmp_file.name
    
    # Ensure all parts have the same offset (critical for proper MIDI timing)
    for part in score.parts:
        part.offset = 0.0
    
    # Convert score to MIDI with proper timing
    score.write('midi', output_path)
    return Path(output_path)


def render_score_audio(score, base_tuning=None, soundfont_path=None):
    """
    Render a Music21 Score directly to WAV with tuning.
    
    Args:
        score: Music21 Score object
        base_tuning: Base tuning frequency (Hz)
        soundfont_path: Path to SoundFont file
        
    Returns:
        Path to WAV file
    """
    if base_tuning is None:
        config = get_config()
        base_tuning = config.audio.base_tuning
    
    # Convert score to MIDI
    midi_path = score_to_midi(score)
    
    # Create temporary WAV file
    wav_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wav_path = Path(wav_tmp.name)
    
    try:
        # Render MIDI to WAV with tuning
        render_audio_with_tuning(
            midi_path=str(midi_path),
            wav_path=str(wav_path),
            base_tuning=base_tuning,
            soundfont_path=soundfont_path
        )
        return wav_path
    finally:
        # Clean up temporary MIDI file
        if midi_path.exists():
            midi_path.unlink()