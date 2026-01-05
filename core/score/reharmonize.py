from music21 import chord, pitch, note

def make_chord(root: str, quality: str) -> chord.Chord:
    """
    Create a chord based on root note and quality.

    Args:
        root (str): Root note of the chord (e.g., 'C', 'D#', 'F').
        quality (str): Chord quality ('major', 'minor', etc.).

    Returns:
        music21.chord.Chord: Constructed chord object.

    Raises:
        ValueError: If root note is invalid.
    """
    base_octave = 4  # Default octave
    try:
        root_pitch = pitch.Pitch(f"{root}{base_octave}")
    except pitch.AccidentalException:
        raise ValueError(f"Invalid root pitch: {root}")

    if quality.lower() == "major":
        new_chord = chord.Chord([root_pitch, root_pitch.transpose(4), root_pitch.transpose(7)])
    elif quality.lower() == "minor":
        new_chord = chord.Chord([root_pitch, root_pitch.transpose(3), root_pitch.transpose(7)])
    else:
        # Default to major if unknown quality
        new_chord = chord.Chord([root_pitch, root_pitch.transpose(4), root_pitch.transpose(7)])

    return new_chord

def replace_chord_in_measure(score, measure_number: int, new_root: str, quality: str = "major"):
    """
    Replace the chord in a specific measure of the score.

    Args:
        score (music21.stream.Score): The score to modify.
        measure_number (int): Measure index (1-based).
        new_root (str): New root note for the chord.
        quality (str, optional): Chord quality. Defaults to "major".
    """
    measure = score.measure(measure_number)
    if measure is None:
        return

    # Remove existing chords
    for c in measure.getElementsByClass(chord.Chord):
        measure.remove(c)

    # Add new chord
    new_ch = make_chord(new_root, quality)
    measure.insert(0, new_ch)

def replace_chords_in_measures(score, replacements: dict):
    """
    Replace multiple chords in a score.

    Args:
        score (music21.stream.Score): Score to modify.
        replacements (dict): Dictionary with measure numbers as keys and
                             (root, quality) tuples as values.
    """
    for measure_number, (root, quality) in replacements.items():
        replace_chord_in_measure(score, measure_number, root, quality)
