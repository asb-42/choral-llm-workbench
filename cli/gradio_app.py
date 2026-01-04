import gradio as gr
from core.score import load_musicxml, write_musicxml
from core.score.reharmonize import replace_chord_in_measure
from llm.ollama_adapter import OllamaAdapter
import tempfile

def reharmonize_gradio(xml_file, measure_number, prompt):
    # Datei laden
    score = load_musicxml(xml_file.name)

    # LLM-Adapter (Stub)
    llm = OllamaAdapter()
    suggestion = llm.generate_harmony(prompt, context={})

    # MVP: letzte Wort des Prompt als Root-Note
    root_note = prompt.strip().split()[-1]

    # Takt ersetzen
    replace_chord_in_measure(score, measure_number, root_note)

    # Temporäre Ausgabe
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
    write_musicxml(score, tmp_file.name)

    return tmp_file.name, f"Applied LLM suggestion: '{root_note}'"

# Gradio UI
iface = gr.Interface(
    fn=reharmonize_gradio,
    inputs=[
        gr.File(label="MusicXML Input"),
        gr.Number(label="Measure Number", value=1),
        gr.Textbox(label="LLM Prompt", placeholder="e.g., Use C major")
    ],
    outputs=[
        gr.File(label="Modified MusicXML Output"),
        gr.Textbox(label="Status")
    ],
    title="Choral LLM Workbench MVP",
    description="Reharmonize a measure in MusicXML using LLM suggestions (stub)."
)

if __name__ == "__main__":
    iface.launch()
