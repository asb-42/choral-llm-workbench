import copy
from music21 import stream

def clone_score(score: stream.Score) -> stream.Score:
    """
    Tiefe Kopie eines music21-Scores für Undo/Redo.
    """
    return copy.deepcopy(score)
