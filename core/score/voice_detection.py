from music21 import stream, note
from typing import Dict


VOICE_RANGES = {
    "soprano": (60, 81),  # C4 – A5
    "alto": (55, 74),     # G3 – D5
    "tenor": (48, 69),    # C3 – A4
    "bass": (36, 60),     # C2 – C4
}


def average_pitch(part: stream.Part) -> float:
    pitches = []
    for n in part.recurse().notes:
        if isinstance(n, note.Note):
            pitches.append(n.pitch.midi)
    if not pitches:
        return -1
    return sum(pitches) / len(pitches)


def detect_voice(part: stream.Part) -> str:
    name = (part.partName or "").lower()

    for voice in ["soprano", "alto", "tenor", "bass"]:
        if voice in name:
            return voice

    avg = average_pitch(part)
    if avg < 0:
        return "unknown"

    for voice, (low, high) in VOICE_RANGES.items():
        if low <= avg <= high:
            return voice

    return "unknown"


def detect_voices(score: stream.Score) -> Dict[str, str]:
    result = {}
    for i, part in enumerate(score.parts):
        label = part.partName or f"Part {i + 1}"
        result[label] = detect_voice(part)
    return result
