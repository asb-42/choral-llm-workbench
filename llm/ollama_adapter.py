from .llm_adapter import LLMAdapter
from typing import Dict, Any

class OllamaAdapter:
    def __init__(self, model_name: str = "mistral"):
        self.model_name = model_name
        # In echten Projekt: hier Ollama-Client initialisieren

    def generate_harmony(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        Stub: gibt einfach den Prompt zurück.
        Später: Integration mit Ollama-API.
        """
        # Für MVP nur Rückgabe des Prompts
        return f"LLM suggestion for prompt: {prompt} (context keys: {list(context.keys())})"
