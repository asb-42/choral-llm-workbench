import requests
import json
from typing import Optional, Tuple, List
from tlr_converter import TLRConverter


class OllamaLLM:
    """Interface to Ollama LLM for musical transformations"""
    
    def __init__(self, model_name: str = "llama3:latest", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.tlr_converter = TLRConverter()
        
        # Fixed system prompt
        self.system_prompt = """You are transforming musical event lists.
Rules:
- Do not remove headers.
- Do not invent measures, parts, or voices.
- Do not create overlapping events.
- Keep durations positive and explicit.
- Output must follow the exact input format.
- If you change harmony, you must emit a HARMONY event.
- Do not encode harmonic changes implicitly via pitch changes alone.
- Use HARMONY events for all harmonic transformations (modulations, chord changes, etc.).
- Harmony events format: HARMONY t=<onset> symbol=<chord> [key=<key_context>]
- Example: HARMONY t=0 symbol=iv key=E minor"""
    
    def transform_music(self, tlr_text: str, instruction: str) -> Tuple[str, List[str]]:
        """Transform music using LLM with given instruction"""
        
        # Build user prompt dynamically
        user_prompt = f"""Transform the following music:
{tlr_text}

Instruction:
{instruction}"""
        
        # Call Ollama API
        response = self._call_ollama(self.system_prompt, user_prompt)
        
        return response.strip(), []
    
    def _call_ollama(self, system_prompt: str, user_prompt: str) -> str:
        """Make API call to Ollama"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model_name,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to call Ollama API: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse Ollama response: {e}")
    
    def set_model(self, model_name: str):
        """Change the LLM model"""
        self.model_name = model_name
    
    def check_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_available_models(self) -> List[dict]:
        """Get list of available models from Ollama"""
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            result = response.json()
            return result.get("models", [])
        except requests.exceptions.RequestException:
            return []