from music21 import chord, note, pitch, stream
from copy import deepcopy

def make_chord(root, quality='major', base_octave=4):
    """
    Erzeugt ein Chord-Objekt aus Root und Quality.
    """
    try:
        root_pitch = pitch.Pitch(f"{root}{base_octave}")
    except Exception:
        raise ValueError(f"Ungültiger Root-Pitch: {root}")

    if quality.lower() == 'major':
        intervals = [0, 4, 7]
    elif quality.lower() == 'minor':
        intervals = [0, 3, 7]
    else:
        intervals = [0, 4, 7]  # default zu major

    pitches = [root_pitch.transpose(i) for i in intervals]
    return chord.Chord(pitches)

def replace_chord_in_measure(score, measure_number, new_root, quality='major'):
    """
    Ersetzt den Akkord in einem bestimmten Takt.
    """
    new_ch = make_chord(new_root, quality)
    try:
        m = score.measure(measure_number)
        # Alte Chords löschen
        for c in m.recurse().getElementsByClass(chord.Chord):
            m.remove(c)
        m.append(new_ch)
    except Exception as e:
        raise ValueError(f"Fehler beim Ersetzen des Chords in Takt {measure_number}: {e}")

def replace_chords_in_measures(score, chords_data):
    """
    Wrapper für mehrere Chord-Ersatz-Aktionen.
    chords_data: Liste von dicts z.B.
        [{'measure': 1, 'root': 'C', 'quality': 'major'}, ...]
    """
    for data in chords_data:
        replace_chord_in_measure(score, data['measure'], data['root'], data.get('quality', 'major'))
    return score
