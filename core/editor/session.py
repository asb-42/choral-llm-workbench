from copy import deepcopy

class EditorSession:
    """
    Verwaltet den aktuellen Score und erlaubt Undo/Redo sowie Ghost-Chords.
    """

    def __init__(self):
        self.current_score = None
        self.history = []
        self.future = []
        self.ghosts = []

    def load_score(self, score):
        """Score in die Session laden und History zurücksetzen"""
        self.current_score = deepcopy(score)
        self.history = [deepcopy(score)]
        self.future = []

    def apply_edit(self, new_score):
        """Neue Version des Scores anwenden"""
        if self.current_score is not None:
            self.history.append(deepcopy(new_score))
            self.future = []
            self.current_score = deepcopy(new_score)

    def undo(self):
        """Letzte Änderung rückgängig machen"""
        if len(self.history) > 1:
            self.future.append(self.history.pop())
            self.current_score = deepcopy(self.history[-1])
        return self.current_score

    def redo(self):
        """Letzte Undo-Operation wiederherstellen"""
        if self.future:
            score = self.future.pop()
            self.history.append(deepcopy(score))
            self.current_score = deepcopy(score)
        return self.current_score

    def add_ghosts(self, ghosts):
        """Liste von Ghost-Chords hinzufügen"""
        self.ghosts = ghosts

    def clear_ghosts(self):
        self.ghosts = []

    def accept_ghost(self, ghost):
        """Ghost-Chord anwenden und aus der Liste entfernen"""
        from core.score.reharmonize import replace_chord_in_measure
        replace_chord_in_measure(self.current_score, ghost.measure, ghost.root)
        if ghost in self.ghosts:
            self.ghosts.remove(ghost)
        self.apply_edit(self.current_score)
