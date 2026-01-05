from core.score.utils import clone_score
from core.editor.ghost import GhostLayer


class EditorSession:
    def __init__(self, score):
        self.history = [clone_score(score)]
        self.index = 0
        self.ghosts = GhostLayer()

    @property
    def current_score(self):
        return self.history[self.index]

    def apply(self, new_score):
        self.history = self.history[: self.index + 1]
        self.history.append(clone_score(new_score))
        self.index += 1

    def undo(self):
        if self.index > 0:
            self.index -= 1

    def redo(self):
        if self.index < len(self.history) - 1:
            self.index += 1

    def clear_ghosts(self):
        self.ghosts.clear()
