from music21 import converter, stream


def load_musicxml(path: str) -> stream.Score:
    """
    Load a MusicXML file and return a music21 Score object.
    """
    score = converter.parse(path)
    if not isinstance(score, stream.Score):
        raise ValueError("Parsed file is not a Score")
    return score
