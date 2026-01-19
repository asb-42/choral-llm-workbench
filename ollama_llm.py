import requests
import json
from typing import Optional, Tuple, List
from tlr_converter import TLRConverter


class OllamaLLM:
    """Interface to Ollama LLM for musical transformations"""
    
    def __init__(self, model_name: str = "qwen2:1.5b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.tlr_converter = TLRConverter()
        
        # Simplified system prompt for small models
        self.system_prompt = """Transform music. ONLY output TLR format.

PART <name> ROLE instrument
VOICE <name>
MEASURE <number> TIME <beats>/<beat-type>
NOTE t=<time> dur=<duration> pitch=<pitch>

NO explanations. ONLY TLR."""
    
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
    
    def _call_ollama(self, system_prompt: str, user_prompt: str, timeout: int = 600) -> str:
        """Make API call to Ollama"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model_name,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.Timeout as e:
            raise RuntimeError(f"LLM inference timeout after {timeout} seconds. Consider using a smaller model or upgrading to GPU acceleration.")
        except requests.exceptions.RequestException as e:
            if "timeout" in str(e).lower():
                raise RuntimeError(f"LLM inference timeout. Try reducing input complexity or use a smaller model.")
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
    
    def explain(self, system_prompt: str, user_prompt: str, timeout: int = 600) -> str:
        """Public method for explanation mode - backward compatibility"""
        return self._call_ollama(system_prompt, user_prompt, timeout)