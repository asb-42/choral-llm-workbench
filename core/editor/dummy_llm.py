# core/editor/dummy_llm.py

from typing import Dict, Union

class DummyLLM:
    """
    Dummy-LLM für Testzwecke.
    Kann entweder einen einzelnen Prompt (str) oder Multi-Prompt (dict pro Stimme) verarbeiten.
    """

    def harmonize_prompt(self, prompt: Union[str, Dict[str, str]]) -> Dict[str, Dict]:
        """
        Harmonisiert basierend auf dem Prompt.

        Parameters:
        -----------
        prompt : str | dict
            Entweder ein einzelner Prompt für alle Stimmen oder ein dict {"S": "...", "A": "...", ...}

        Returns:
        --------
        Dict[str, Dict]: Dummy-Harmonisierungsinformationen pro Stimme.
        """
        # Dummy-Logik: fixe Akkorde pro Stimme
        default_chords = {
            "S": {"measure": 1, "root": "C", "quality": "major"},
            "A": {"measure": 1, "root": "G", "quality": "major"},
            "T": {"measure": 1, "root": "E", "quality": "major"},
            "B": {"measure": 1, "root": "C", "quality": "major"},
        }

        if isinstance(prompt, str):
            # Single prompt für alle Stimmen -> gleiche Chords
            return default_chords
        elif isinstance(prompt, dict):
            # Multi-Prompt: jede Stimme bekommt Dummy-Werte + Logik pro Stimme
            output = {}
            for voice, voice_prompt in prompt.items():
                # Dummy-Logik: nur Buchstaben der Stimme ändern, um zu variieren
                root = default_chords.get(voice, {"root": "C"})["root"]
                output[voice] = {"measure": 1, "root": root, "quality": "major"}
            return output
        else:
            raise ValueError("Prompt muss ein str oder dict sein")
