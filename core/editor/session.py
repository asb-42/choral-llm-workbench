from copy import deepcopy

class EditorSession:
    """Class to manage an editing session for a musical score."""

    def __init__(self):
        self.current_score = None
        self.history = []
        self.future = []

    def load_score(self, score):
        """
        Load a score into the session and reset history.

        Args:
            score (music21.stream.Score): The score to load.
        """
        self.current_score = deepcopy(score)
        self.history = [deepcopy(score)]
        self.future = []

    def save_state(self):
        """Save the current score to the history stack."""
        if self.current_score is not None:
            self.history.append(deepcopy(self.current_score))
            self.future = []

    def undo(self):
        """
        Undo the last change and move it to the future stack.

        Returns:
            music21.stream.Score | None: The previous score state or None if not available.
        """
        if len(self.history) > 1:
            self.future.append(self.history.pop())
            self.current_score = deepcopy(self.history[-1])
            return self.current_score
        return None

    def redo(self):
        """
        Redo the last undone change.

        Returns:
            music21.stream.Score | None: The next score state or None if not available.
        """
        if self.future:
            self.current_score = self.future.pop()
            self.history.append(deepcopy(self.current_score))
            return self.current_score
        return None
