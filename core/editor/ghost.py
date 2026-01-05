from dataclasses import dataclass


@dataclass
class GhostChord:
    measure: int
    root: str
    quality: str = "major"

    def label(self):
        return f"Takt {self.measure}: {self.root} {self.quality}"


class GhostLayer:
    def __init__(self):
        self.chords = []

    def add(self, ghost: GhostChord):
        self.chords.append(ghost)

    def clear(self):
        self.chords = []

    def list_labels(self):
        return [g.label() for g in self.chords]
