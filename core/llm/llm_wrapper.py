# Datei: core/llm/llm_wrapper.py

import json
import subprocess

class BaseLLM:
    """Basisklasse für beliebige LLMs"""
    def harmonize_prompt(self, prompt_text):
        raise NotImplementedError()

class DummyLLM(BaseLLM):
    def harmonize_prompt(self, prompt_text):
        root_map = {"C":"C", "D":"D", "E":"E", "F":"F", "G":"G", "A":"A", "B":"B"}
        root = prompt_text[0].upper()
        if root not in root_map:
            root = "C"
        return {"measure": 1, "root": root, "quality": "major"}

class OllamaLLM(BaseLLM):
    """LLM-Anbindung via Ollama CLI"""
    def __init__(self, model_name="mistral-7b"):
        self.model_name = model_name

    def harmonize_prompt(self, prompt_text):
        """
        Übergibt Prompt an lokales Ollama-Modell.
        Erwartete Antwort: JSON {"measure": int, "root": "C", "quality": "major"}
        """
        try:
            # Ollama CLI-Aufruf
            result = subprocess.run(
                ["ollama", "eval", self.model_name, "--json", prompt_text],
                capture_output=True,
                text=True,
                check=True
            )
            # Ollama liefert JSON aus
            response_json = result.stdout.strip()
            response = json.loads(response_json)
            return response
        except Exception as e:
            print(f"[LLM ERROR] {e}")
            # Fallback auf Dummy
            return {"measure": 1, "root": "C", "quality": "major"}
