from .llm_adapter import LLMAdapter
from typing import Dict, Any

class OllamaAdapter:
    def generate_harmony(self, prompt: str, context: dict = {}):
        """
        Stub: LLM generiert Akkorde pro Stimme.
        Erwartet prompt: "Make measure 1-2 more romantic"
        Rückgabe: dict {'S': ['Cmaj','Dmaj'], 'A':['G','A'], ...}
        """
        # TODO: echte LLM-Integration
        # Für MVP: Dummy-Akkorde
        return {
            "S": ["Cmaj","Dmaj"],
            "A": ["G","A"],
            "T": ["E","F"],
            "B": ["C","D"]
        }
