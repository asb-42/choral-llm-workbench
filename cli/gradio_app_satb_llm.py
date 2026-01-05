# cli/gradio_app_satb_llm.py

import gradio as gr
from core.score import load_musicxml, write_musicxml, replace_chord_in_measure
from core.editor.dummy_llm import DummyLLM
from copy import deepcopy
import tempfile
import os

# Dummy-LLM initialisieren
dummy_llm = DummyLLM()

def harmonize_multi_voice(score_file, prompts_input):
    try:
        # Score laden
        score = load_musicxml(score_file.name)

        # Prompts parsen: Input als Dict, z.B. {"S": "...", "A": "...", ...}
        prompts = prompts_input
        if isinstance(prompts_input, str):
            # Falls als JSON-String reinkommt
            import json
            prompts = json.loads(prompts_input)

        # Harmonisierung mit Dummy-LLM
        results = dummy_llm.harmonize_prompt(prompts)

        # Dummy: Chords ins Score einfügen
        harmonized_score = deepcopy(score)
        for voice, chord_info in results.items():
            replace_chord_in_measure(harmonized_score,
                                     chord_info["measure"],
                                     chord_info["root"])

        # Score temporär speichern
        tmp_xml = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
        write_musicxml(harmonized_score, tmp_xml.name)

        # Audio-Preview: hier Dummy, kein echtes Audio
        tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp_wav.write(b"Dummy audio data")  # Platzhalter
        tmp_wav.close()

        return tmp_xml.name, tmp_wav.name, str(results)

    except Exception as e:
        return None, None, f"Error harmonizing: {str(e)}"

# Gradio-Interface
with gr.Blocks() as demo:
    gr.Markdown("# SATB Harmonization (Dummy-LLM)")
    score_input = gr.File(label="MusicXML Score")
    prompts_input = gr.Textbox(label="Prompts per Voice (JSON)", value='{"S":"Make measure 1 more romantic","A":"...","T":"...","B":"..."}')
    output_file = gr.File(label="Harmonized Score")
    output_audio = gr.Audio(label="Audio Preview")
    output_text = gr.Textbox(label="LLM Output")

    btn = gr.Button("Harmonize")
    btn.click(
        harmonize_multi_voice,
        inputs=[score_input, prompts_input],
        outputs=[output_file, output_audio, output_text]
    )

if __name__ == "__main__":
    demo.launch()
