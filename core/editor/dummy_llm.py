"""
Dummy LLM module for testing harmonization functionality.

This class provides a mock interface for an LLM that generates chord suggestions
based on textual prompts. It is meant for development and testing purposes only.
"""

from typing import Dict

class DummyLLM:
    """
    Dummy Language Model for chord harmonization.
    """

    def __init__(self):
        """
        Initialize the dummy LLM.
        """
        # In a real LLM, you might load model weights or connect to an API
        self.name = "DummyLLM"

    def harmonize_prompt(self, prompt: str) -> Dict[str, str]:
        """
        Generate a chord suggestion for a single-voice prompt.

        Args:
            prompt (str): A textual prompt describing the desired harmonization.

        Returns:
            dict: Dictionary with measure info and chord suggestion.
                  Example: {'measure': 1, 'root': 'C', 'quality': 'major'}
        """
        # This is a fixed dummy implementation
        return {'measure': 1, 'root': 'C', 'quality': 'major'}

    def harmonize_multi_voice(self, prompts: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """
        Generate chord suggestions for multiple voices.

        Args:
            prompts (dict): Dictionary mapping voice names ('S','A','T','B') to prompts.

        Returns:
            dict: Dictionary mapping voice -> chord suggestion.
                  Example:
                  {
                      'S': {'measure': 1, 'root': 'C', 'quality': 'major'},
                      'A': {'measure': 1, 'root': 'G', 'quality': 'major'},
                      'T': {'measure': 1, 'root': 'E', 'quality': 'major'},
                      'B': {'measure': 1, 'root': 'C', 'quality': 'major'}
                  }
        """
        # Generate a simple default for testing
        return {voice: {'measure': 1, 'root': 'C', 'quality': 'major'} for voice in prompts}
