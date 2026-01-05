# __init__.py für core.score
from .parser import load_musicxml, write_musicxml
from .harmony import analyze_chords
from .reharmonize import replace_chord_in_measure  # nur die existierende Funktion importieren
# von hier aus können andere Module spezifische Funktionen importieren
from .llm import apply_llm_chords_to_measures
