from core.editor.session import EditorSession
from core.score.reharmonize import replace_chord_in_measure
from core.score.parser import load_musicxml
from typing import Dict

class SATBLLM:
    """
    Schnittstelle für LLM-basierte Harmonisierung von SATB-Scores.
    """

    def __init__(self, session: EditorSession, llm_interface):
        """
        session: EditorSession-Objekt
        llm_interface: Objekt, das die LLM-Kommunikation kapselt (z.B. Ollama)
        """
        self.session = session
        self.llm = llm_interface

    def harmonize_prompt(self, measure_number: int, prompt: str):
        """
        LLM aufrufen und neuen Akkord für den angegebenen Takt erzeugen
        """
        # LLM-Response simulieren
        # Erwartet Rückgabe z.B. {"root": "A", "quality": "minor"}
        response = self.llm.generate_chord(prompt)

        if not response or "root" not in response:
            raise ValueError("LLM konnte keinen Root-Akkord bestimmen")

        new_root = response["root"]
        quality = response.get("quality", "major")
        chord_name = new_root if quality == "major" else new_root + "m"

        replace_chord_in_measure(self.session.current_score, measure_number, chord_name)
        self.session.apply_edit(self.session.current_score)
        return chord_name

    def harmonize_multiple(self, prompts: Dict[int, str]):
        """
        Mehrere Takte gleichzeitig harmonisieren
        prompts: dict von measure_number -> Prompt
        """
        results = {}
        for measure, prompt in prompts.items():
            chord_name = self.harmonize_prompt(measure, prompt)
            results[measure] = chord_name
        return results
