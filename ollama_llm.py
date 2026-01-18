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
        self.system_prompt = """You are transforming musical event lists (TLR format).

CRITICAL FORMAT REQUIREMENTS:
- EVERY line must be a valid TLR event: NOTE, REST, HARMONY, or LYRIC
- Headers MUST be on separate lines: MEASURE <number> or VOICE <name>
- NO parenthetical information like (Voice 1) - use separate VOICE lines
- NO figured bass notation like [FIGURED BASS: ...] - use HARMONY events only
- Events MUST follow exact format:
  * NOTE t=<onset> dur=<duration> pitch=<pitch> [voice=<voice>]
  * REST t=<onset> dur=<duration>
  * HARMONY t=<onset> symbol=<chord> [key=<key>]
  * LYRIC t=<onset> text="<lyric>"

STRICT RULES:
- Do NOT remove MEASURE or VOICE headers
- Do NOT invent new measures, parts, or voices
- Do NOT create overlapping events
- Keep durations positive (fractions like 1/4, 1/2, 1)
- Do NOT embed voice information in NOTE events
- Do NOT write explanations or narrative text
- Output ONLY valid TLR events - no comments, no explanations

HARMONY RULES:
- All harmonic changes MUST use HARMONY events only
- NEVER encode harmony changes via pitch changes alone
- Format: HARMONY t=<onset> symbol=<chord> [key=<key>]

EXAMPLE OUTPUT FORMAT:
MEASURE 1
VOICE Soprano
NOTE t=0 dur=1 pitch=C4
NOTE t=1 dur=1 pitch=D4
VOICE Alto
NOTE t=0 dur=1 pitch=G3
NOTE t=1 dur=1 pitch=A3
HARMONY t=0 symbol=C

DO NOT OUTPUT:
- Any narrative explanations
- Comments about what you did
- Figured bass notation
- Parenthetical voice information
- Any text that is not a valid TLR event"""
    
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
            response = requests.post(url, json=payload, timeout=300)  # Increased timeout for CPU inference
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.Timeout as e:
            raise RuntimeError(f"LLM inference timeout after 300 seconds. Consider using a smaller model or upgrading to GPU acceleration.")
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
    
    def explain(self, system_prompt: str, user_prompt: str, timeout: int = 300) -> str:
        """Public method for explanation mode - backward compatibility"""
        return self._call_ollama(system_prompt, user_prompt, timeout)