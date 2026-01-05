# core/editor/dummy_llm.py

class DummyLLM:
    """
    Dummy LLM for testing purposes.
    Returns fixed harmonization outputs, optionally per voice.
    """

    def __init__(self):
        # Optional: kann internal state oder history speichern
        self.history = []

    def harmonize_prompt(self, prompt: str, voice: str = None):
        """
        Harmonize a given prompt.

        Args:
            prompt (str): The textual prompt to harmonize.
            voice (str, optional): Voice identifier ('S', 'A', 'T', 'B').
                                   Ignored in dummy implementation.

        Returns:
            dict: Dummy harmonization output.
        """
        # Speichere Prompt in history (optional)
        self.history.append({"prompt": prompt, "voice": voice})

        # Dummy harmonization: immer Measure 1, Root C, Quality major
        result = {
            "measure": 1,
            "root": "C",
            "quality": "major"
        }

        return result
