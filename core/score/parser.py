from music21 import converter

def load_musicxml(path: str):
    """Lädt eine MusicXML-Datei und gibt ein music21 Stream-Objekt zurück"""
    score = converter.parse(path)
    return score

def write_musicxml(score, path: str):
    """
    Speichert ein music21 Stream-Objekt als MusicXML
    """
    score.write('musicxml', fp=path)
