from typing import Protocol, Dict, Any

class LLMAdapter(Protocol):
    """
    Interface for LLMs.
    """
    def generate_harmony(self, prompt: str, context: Dict[str, Any]) -> str:
        ...
