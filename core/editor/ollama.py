import subprocess
from typing import List

# Optional: Du kannst hier deinen bevorzugten LLM-Wrapper importieren
# Beispiel: from llm_ollama import OllamaLLM


def list_ollama_models() -> List[str]:
    """
    List all locally installed Ollama models.
    
    Returns:
        List of model names as strings.
    """
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.splitlines()
        # Filter empty lines and header lines
        models = [line.strip() for line in lines if line.strip() and not line.startswith("Name")]
        return models
    except subprocess.CalledProcessError as e:
        print("Error listing Ollama models:", e)
        return []
    except FileNotFoundError:
        print("Ollama CLI not found. Is Ollama installed?")
        return []


class OllamaDummyLLM:
    """
    Minimal dummy wrapper for testing.
    In production, replace with a proper LLM client for Ollama.
    """
    def __init__(self, model_name: str):
        self.model_name = model_name

    def harmonize_prompt(self, prompt: str) -> dict:
        """
        Fake harmonization output for testing purposes.
        Replace this with a real call to Ollama LLM.
        """
        return {
            "S": {"measure": 1, "root": "C", "quality": "major"},
            "A": {"measure": 1, "root": "G", "quality": "major"},
            "T": {"measure": 1, "root": "E", "quality": "major"},
            "B": {"measure": 1, "root": "C", "quality": "major"},
        }


def get_ollama_llm(model_name: str):
    """
    Returns an instance of the selected Ollama LLM.
    Replace with real Ollama client if available.
    """
    # TODO: Replace OllamaDummyLLM with actual Ollama LLM API
    return OllamaDummyLLM(model_name)
