# core/editor/dummy_llm.py
from typing import Optional, Dict, Any

class DummyLLM:
    """
    Dummy LLM for testing purposes.
    Returns fixed harmonization outputs, optionally per voice.
    """

    def __init__(self):
        # Optional: kann internal state oder history speichern
        self.history = []

    def harmonize_prompt(self, prompt: str, voice: Optional[str] = None):
        """
        Harmonize a given prompt.

        Args:
            prompt (str): The textual prompt to harmonize.
            voice (str, optional): Voice identifier ('S', 'A', 'T', 'B').
                                   Ignored in dummy implementation.

        Returns:
            dict: Dummy harmonization output.
        """
        # Speichere Prompt in history (optional)
        self.history.append({"prompt": prompt, "voice": voice})

        # Dummy harmonization: immer Measure 1, Root C, Quality major
        result = {
            "measure": 1,
            "root": "C",
            "quality": "major"
        }

        return result
    
    def harmonize_multi_voice(self, prompts: Dict[str, str]) -> Dict[str, Any]:
        """
        Harmonize multiple voices with their respective prompts.
        
        Args:
            prompts (dict): Dictionary with voice keys ('S', 'A', 'T', 'B') and prompt values
            
        Returns:
            dict: Dictionary with voice suggestions
        """
        # Store all prompts in history
        for voice, prompt in prompts.items():
            self.history.append({"prompt": prompt, "voice": voice})
        
        # Generate dummy suggestions for each voice
        suggestions = {}
        for voice, prompt in prompts.items():
            suggestions[voice] = {
                "measure": 1,
                "root": "C",
                "quality": "major",
                "prompt_used": prompt
            }
        
        return suggestions
