from music21 import chord, note, pitch

# Hilfsfunktion: Akkord aus Root und Qualität
def make_chord(root: str, quality: str = "major"):
    """
    root: Grundton, z.B. 'A' oder 'F'
    quality: 'major' oder 'minor'
    """
    base_octave = 4
    try:
        root_pitch = pitch.Pitch(f"{root}{base_octave}")
    except Exception:
        raise ValueError(f"Ungültiger Root-Pitch: {root}")

    # Intervalle für Dur/Moll
    if quality.lower() == "major":
        intervals = [0, 4, 7]  # Grundton, große Terz, Quinte
    else:
        intervals = [0, 3, 7]  # Grundton, kleine Terz, Quinte

    notes = [note.Note(root_pitch.transpose(i)) for i in intervals]
    return chord.Chord(notes)


def replace_chord_in_measure(score, measure_number, new_root_with_quality):
    """
    Ersetzt Akkord in allen Stimmen eines Taktes.
    new_root_with_quality: z.B. "Am" oder "F"
    """
    # Root und Qualität trennen
    if new_root_with_quality.endswith("m"):
        root = new_root_with_quality[:-1]
        quality = "minor"
    else:
        root = new_root_with_quality
        quality = "major"

    # Akkord erzeugen
    new_ch = make_chord(root, quality)

    # Takt in allen Stimmen ersetzen
    for p in score.parts:
        measure = p.measure(measure_number)
        if measure is not None:
            # Alte Noten löschen
            for n in list(measure.notes):
                measure.remove(n)
            measure.insert(0, new_ch)
