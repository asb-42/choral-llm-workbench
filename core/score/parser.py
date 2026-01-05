from music21 import converter, stream

def load_musicxml(file_path: str) -> stream.Score:
    """
    Load a MusicXML file and return a music21 Score object.

    Args:
        file_path (str): Path to the MusicXML file.

    Returns:
        music21.stream.Score: Parsed score object.
    """
    score = converter.parse(file_path)
    return score

def write_musicxml(score: stream.Score, file_path: str):
    """
    Write a music21 Score object to a MusicXML file.

    Args:
        score (music21.stream.Score): Score to export.
        file_path (str): Destination file path.
    """
    score.write('musicxml', fp=file_path)

