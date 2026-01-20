import requests
import json
from typing import Optional, Tuple, List, Union
from tlr_converter import TLRConverter


class OllamaLLM:
    """Interface to Ollama LLM for musical transformations"""
    
    def __init__(self, model_name: str = "qwen2:1.5b", base_url: Optional[str] = None):
        from user_config import get_ollama_base_url
        self.model_name = model_name
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = get_ollama_base_url()
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
    
    def set_base_url(self, host: str, port: str = "11434"):
        """Update the base URL with new host/port"""
        self.base_url = f"http://{host}:{port}"
    
    def get_available_models_with_info(self):
        """Get list of available models with formatted information"""
        try:
            url = f"{self.base_url}/api/tags"
            print(f"DEBUG: Getting models from {url}")
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            print(f"DEBUG: Response status: {response.status_code}")
            result = response.json()
            models = result.get("models", [])
            print(f"DEBUG: Found {len(models)} raw models")
            
            # Format model information for display
            formatted_models = []
            for model in models:
                name = model.get('name', model.get('model', 'unknown'))
                size_bytes = model.get('size', 0)
                
                # Convert bytes to human-readable format
                if size_bytes >= 1024 * 1024 * 1024:
                    size_str = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
                elif size_bytes >= 1024 * 1024:
                    size_str = f"{size_bytes / (1024 * 1024):.0f} MB"
                else:
                    size_str = f"{size_bytes / 1024:.0f} KB"
                
                # Get additional details
                details = model.get('details', {})
                param_size = details.get('parameter_size', 'N/A')
                quantization = details.get('quantization_level', 'N/A')
                
                # Create display string
                display_str = f"{name} ({param_size}, {quantization}, {size_str})"
                formatted_models.append({
                    'name': name,
                    'display': display_str,
                    'size': size_str,
                    'param_size': param_size,
                    'quantization': quantization,
                    'full_model': model
                })
            
            print(f"DEBUG: Formatted {len(formatted_models)} models")
            return formatted_models
            
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Error getting models: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error in get_models: {e}")
            return []
    
    def check_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            url = f"{self.base_url}/api/tags"
            print(f"DEBUG: Checking connection to {url}")
            response = requests.get(url, timeout=5)
            print(f"DEBUG: Response status: {response.status_code}")
            
            # Check if we got valid JSON response
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'models' in data:
                        print(f"DEBUG: Got {len(data['models'])} models")
                        return True
                    else:
                        print(f"DEBUG: Invalid response format: {response.text[:100]}")
                        return False
                except json.JSONDecodeError as e:
                    print(f"DEBUG: JSON decode error: {e}")
                    print(f"DEBUG: Response text: {response.text[:200]}")
                    return False
            else:
                print(f"DEBUG: HTTP error {response.status_code}: {response.text[:100]}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Connection error: {e}")
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