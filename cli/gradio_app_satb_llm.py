import json
import tempfile
import gradio as gr
from core.editor.session import EditorSession
from core.score.parser import load_musicxml, write_musicxml
from core.score.reharmonize import replace_chord_in_measure

# --- Dummy-LLM ---
class DummyLLM:
    """
    Simuliert Harmonisierung für mehrere Stimmen.
    Gibt pro Stimme eine Liste von Akkord-Änderungen zurück.
    """
    def harmonize_prompt(self, prompt):
        """
        prompt: str, z.B. "Make measure 1 more romantic"
        Rückgabe: dict mit root, quality, measure
        """
        prompt_lower = prompt.lower()
        if "bright" in prompt_lower:
            return {"root": "C", "quality": "maj", "measure": 1}
        elif "passing" in prompt_lower:
            return {"root": "G", "quality": "maj", "measure": 2}
        elif "romantic" in prompt_lower:
            return {"root": "Am", "quality": "min", "measure": 3}
        elif "stable" in prompt_lower:
            return {"root": "F", "quality": "maj", "measure": 4}
        else:
            # Default fallback
            return {"root": "C", "quality": "maj", "measure": 1}

llm = DummyLLM()
session = EditorSession()

# --- Hilfsfunktion ---
def harmonize_multi_voice(file, prompts_json):
    """
    Score laden und Multi-Voice Harmonisierung durchführen.
    """
    # Score laden
    score = load_musicxml(file.name)
    if score is None:
        return None, None, "Fehler: Score konnte nicht geladen werden"
    session.load_score(score)

    try:
        prompts = json.loads(prompts_json)
    except Exception as e:
        return None, None, f"Fehler beim Parsen der Prompts: {e}"

    # Dummy-Harmonisierung pro Stimme
    for voice, prompt in prompts.items():
        chord_info = llm.harmonize_prompt(prompt)
        measure_number = chord_info.get("measure", 1)
        root = chord_info.get("root", "C")
        quality = chord_info.get("quality", "maj")
        try:
            replace_chord_in_measure(session.current_score, measure_number, root, quality, voice=voice)
        except Exception as e:
            return None, None, f"Fehler beim Ersetzen des Akkords für {voice}: {e}"

    # Aktualisierte Score-Datei erstellen
    tmp_score_file = tempfile.NamedTemporaryFile(suffix=".xml", delete=False)
    write_musicxml(session.current_score, tmp_score_file.name)

    # Dummy Audio-Preview als WAV (optional kann echte Synthese ergänzt werden)
    tmp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp_audio_file.write(b"")  # leer, Platzhalter
    tmp_audio_file.close()

    return tmp_score_file.name, tmp_audio_file.name, "Harmonisierung abgeschlossen!"

# --- Gradio-Interface ---
with gr.Blocks() as app:
    gr.Markdown("## SATB Harmonizer mit Multi-Prompts")
    with gr.Row():
        upload_file = gr.File(label="MusicXML / MXL Score", file_types=[".xml", ".mxl"])
        voice_prompts = gr.Textbox(
            label="Prompts per Voice (JSON)",
            value='{"S": "bright", "A": "passing tone", "T": "romantic", "B": "stable"}',
            placeholder='{"S":"", "A":"", "T":"", "B":""}'
        )
    with gr.Row():
        btn_submit = gr.Button("Harmonize")
    with gr.Row():
        out_file = gr.File(label="Updated Score")
        out_audio = gr.Audio(label="Preview")
        out_log = gr.Textbox(label="Log")

    btn_submit.click(
        fn=harmonize_multi_voice,
        inputs=[upload_file, voice_prompts],
        outputs=[out_file, out_audio, out_log]
    )

if __name__ == "__main__":
    app.launch()
