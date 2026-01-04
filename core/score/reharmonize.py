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

def replace_chords_in_measures(score: stream.Score, measures: list[int], roots_per_voice: dict):
    """
    Reharmonize multiple measures and voices.

    :param score: music21 Score
    :param measures: list of measure numbers
    :param roots_per_voice: dict like {'S': ['C','D'], 'A': ['G','A'], ...}
        Each list must match the number of measures
    """
    parts = {p.id: p for p in score.parts}  # assumes part.id = S/A/T/B

    for voice, roots in roots_per_voice.items():
        if voice not in parts:
            continue
        part = parts[voice]
        for idx, measure_num in enumerate(measures):
            if idx >= len(roots):
                continue
            root = roots[idx]
            m = part.measure(measure_num)
            if m is None:
                continue
            # Vereinfachtes Akkord-Setzen: nur Grundton + Terz + Quinte
            new_chord = chord.Chord([root, root+'3', root+'5'])
            m.notes = [new_chord]  # ersetzt alle Noten im Takt

def apply_llm_chords_to_measures(score: stream.Score, measures: list[int], chords_per_voice: dict):
    """
    Wendet die vom LLM gelieferten Akkorde pro Stimme auf mehrere Takte an.
    
    :score: music21.Score
    :measures: Liste von Taktzahlen
    :chords_per_voice: dict wie {'S': ['Cmaj', 'Dmin'], 'A': ['Gmaj', 'Amin'], ...}
        Jeder Eintrag entspricht der Anzahl der measures
    """
    # Teile nach Stimme
    parts = {p.id: p for p in score.parts}  # assumes part.id = S/A/T/B

    for voice, chord_list in chords_per_voice.items():
        if voice not in parts:
            continue
        part = parts[voice]

        for idx, measure_num in enumerate(measures):
            if idx >= len(chord_list):
                continue
            chord_str = chord_list[idx]

            m = part.measure(measure_num)
            if m is None:
                continue

            # LLM liefert z.B. "Cmaj", "Dmin7", "G7"
            # Konvertiere in music21.Chord
            try:
                c = chord.Chord(chord_str)
            except Exception:
                # Fallback: Grundton
                c = chord.Chord([chord_str[0]])  # nur Root

            # Alle Noten im Takt ersetzen
            m.notes = [c]

def update_single_measure(score: stream.Score, measure_number: int, chords_per_voice: dict):
    """
    Aktualisiert einen einzelnen Takt in allen SATB-Stimmen.

    :score: music21.Score
    :measure_number: int
    :chords_per_voice: dict {'S': 'Cmaj', 'A': 'G', 'T':'E', 'B':'C'}
    """
    parts = {p.id: p for p in score.parts}  # assumes part.id = S/A/T/B

    for voice, chord_str in chords_per_voice.items():
        if voice not in parts:
            continue
        part = parts[voice]
        m = part.measure(measure_number)
        if m is None:
            continue
        try:
            c = chord.Chord(chord_str)
        except Exception:
            c = chord.Chord([chord_str[0]])  # fallback auf Root
        m.notes = [c]
