from music21 import stream, chord, harmony

def analyze_chords(score: stream.Score) -> dict:
    """
    Return a dictionary: {measure_number: chord_symbol}
    for each measure in the score.
    """
    chords_per_measure = {}

    # Wir betrachten nur die erste Stimme pro Part (vereinfacht)
    for measure in score.parts[0].getElementsByClass(stream.Measure):
        measure_number = measure.number
        c = chord.Chord(measure.notes)
        if len(c.pitches) == 0:
            chords_per_measure[measure_number] = "N.C."
            continue
        # --- try/except korrekt eingerückt ---
        try:
            cs = harmony.chordSymbolFromChord(c)
            chords_per_measure[measure_number] = cs.figure
        except Exception:
            chords_per_measure[measure_number] = "unknown"

    return chords_per_measure
