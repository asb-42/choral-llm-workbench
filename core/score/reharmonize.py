from music21 import chord, note, pitch, stream
from copy import deepcopy

def make_chord(root: str, quality: str, base_octave: int = 4) -> chord.Chord:
    """
    Create a chord given its root note and quality.

    Args:
        root (str): Root note of the chord (e.g., 'C', 'D#').
        quality (str): Chord quality ('major', 'minor', 'dim', etc.).
        base_octave (int, optional): Octave number for the chord root. Defaults to 4.

    Returns:
        music21.chord.Chord: The generated chord.
    """
    try:
        root_pitch = pitch.Pitch(f"{root}{base_octave}")
    except Exception:
        raise ValueError(f"Invalid root pitch: {root}")

    if quality.lower() == 'major':
        intervals = [0, 4, 7]
    elif quality.lower() == 'minor':
        intervals = [0, 3, 7]
    elif quality.lower() == 'dim':
        intervals = [0, 3, 6]
    else:
        raise ValueError(f"Unsupported chord quality: {quality}")

    chord_notes = [note.Note(root_pitch.midi + i) for i in intervals]
    return chord.Chord(chord_notes)

def replace_chord_in_measure(score: stream.Score, measure_number: int, new_root: str, new_quality: str = 'major'):
    """
    Replace the chord in a specific measure with a new chord.

    Args:
        score (music21.stream.Score): The score containing the measure.
        measure_number (int): Number of the measure to replace.
        new_root (str): Root note of the new chord.
        new_quality (str, optional): Quality of the new chord. Defaults to 'major'.
    """
    measure = score.measure(measure_number)
    if measure is None:
        raise ValueError(f"Measure {measure_number} not found in score.")

    new_ch = make_chord(new_root, new_quality)
    # Remove existing chords
    for c in measure.getElementsByClass(chord.Chord):
        measure.remove(c)

    # Insert the new chord at the beginning of the measure
    measure.insert(0, new_ch)

def replace_chords_in_measures(score: stream.Score, replacements: dict):
    """
    Replace chords in multiple measures according to a dictionary mapping.

    Args:
        score (music21.stream.Score): The score to modify.
        replacements (dict): Dictionary mapping measure_number -> (root, quality)
    """
    for measure_num, (root, quality) in replacements.items():
        replace_chord_in_measure(score, measure_num, root, quality)
