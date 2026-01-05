from music21 import harmony, chord, stream

def analyze_chords(score: stream.Score):
    """
    Analyze the chords of a score and return a list of chord symbols.

    Args:
        score (music21.stream.Score): The score to analyze.

    Returns:
        List[music21.harmony.ChordSymbol]: List of chord symbols in the score.
    """
    chords_list = []
    for c in score.chords:  # Iterate over all chords in the score
        try:
            cs = harmony.chordSymbolFromChord(c)
            chords_list.append(cs)
        except Exception:
            # Skip chords that cannot be analyzed
            continue
    return chords_list
