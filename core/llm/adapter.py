from typing import Dict

from core.llm.llm_wrapper import OllamaLLM


class LLMAdapter:
    """Adapter to unify LLM backends (currently Ollama).

    This adapter provides a uniform API for the rest of the pipeline,
    allowing us to swap backends (dummy, Ollama, etc.) with minimal changes
    to the caller code.
    """

    def __init__(self, model_name: str = "mistral-7b"):
        self.model_name = model_name
        # Ollama wrapper handles the actual local model invocation
        self.llm = OllamaLLM(model_name=model_name)

    def harmonize_multi_voice(self, prompts: Dict[str, str]) -> Dict[str, Dict]:
        """Harmonize multiple voices given per-voice prompts.

        Args:
            prompts: Mapping from voice key (e.g. 'S', 'A', 'T', 'B') to prompt text.

        Returns:
            Dict[str, dict]: Per-voice LLM responses. Expected keys per voice:
                - measure (int)
                - root (str)
                - quality (str)
        """
        results: Dict[str, Dict] = {}
        for voice, prompt in prompts.items():
            try:
                # Let the underlying LLM produce a chord for this voice
                data = self.llm.harmonize_prompt(f"{prompt} (voice: {voice})")
            except Exception as e:
                # Fallback to a safe default to keep the workflow running
                print(f"[LLMAdapter] Harmonization failed for {voice}: {e}")
                data = {"measure": 1, "root": "C", "quality": "major"}
            results[voice] = data
        return results
