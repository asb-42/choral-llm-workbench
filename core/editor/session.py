# core/editor/session.py

from copy import deepcopy

class Session:
    """
    Holds the current score, history, and future states
    for undo/redo functionality.
    """

    def __init__(self):
        self.current_score = None
        self.history = []
        self.future = []

    def load_score(self, score):
        """
        Load a score into the session and reset history.
        """
        self.current_score = deepcopy(score)
        self.history = [deepcopy(score)]
        self.future = []

    def save_state(self):
        """
        Save current score state to history.
        """
        self.history.append(deepcopy(self.current_score))
        self.future = []

    def undo(self):
        """
        Undo the last change.
        """
        if len(self.history) > 1:
            self.future.append(self.history.pop())
            self.current_score = deepcopy(self.history[-1])
        else:
            print("Nothing to undo")

    def redo(self):
        """
        Redo the last undone change.
        """
        if self.future:
            self.history.append(self.future.pop())
            self.current_score = deepcopy(self.history[-1])
        else:
            print("Nothing to redo")
