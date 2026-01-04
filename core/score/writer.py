from music21 import stream


def write_musicxml(score: stream.Score, path: str) -> None:
    """
    Write a music21 Score object to a MusicXML file.
    """
    score.write(fmt="musicxml", fp=path)
