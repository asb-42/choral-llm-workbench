from music21 import stream, chord, note

def replace_chord_in_measure(score: stream.Score, measure_number: int, new_root: str) -> None:
    """
    Replace all notes in a measure with a single triad based on new_root.
    Only modifies the first part for simplicity.
    """
    part = score.parts[0]
    measure = part.measure(measure_number)

    if measure is None:
        raise ValueError(f"Measure {measure_number} not found.")

    # Entferne alte Noten
    for n in list(measure.notes):
        measure.remove(n)

    # Erzeuge einfache Dur-Triade
    new_chord = chord.Chord([new_root, new_root + '3', new_root + '5'])
    new_chord.quarterLength = 1.0  # Notenlänge 1 Viertelnote pro Ton
    measure.insert(0, new_chord)
