import gradio as gr
from core.editor.session import EditorSession
from core.score.parser import load_musicxml, write_musicxml
from core.llm.satb import SATBLLM

# Dummy LLM für Demo – später durch Ollama oder anderes LLM ersetzen
class DummyLLM:
    def generate_chord(self, prompt):
        # Einfaches Mapping für Demo
        mapping = {
            "romantic": {"root": "A", "quality": "minor"},
            "bright": {"root": "C", "quality": "major"},
        }
        for key in mapping:
            if key in prompt.lower():
                return mapping[key]
        return {"root": "C", "quality": "major"}

# Globale Session initialisieren
session = EditorSession()
llm = DummyLLM()
satb_llm = SATBLLM(session, llm)

def load_score(file):
    try:
        # Music21 erkennt MXL und MusicXML automatisch
        score = load_musicxml(file.name)
        if score is None:
            return "Fehler: Score konnte nicht geladen werden", None
        # Score in Session laden
        session.load_score(score)
        return "Score erfolgreich geladen!", file
    except Exception as e:
        return f"Fehler beim Laden des Scores: {str(e)}", None

def harmonize_takt(measure_number, prompt):
    try:
        chord_name = satb_llm.harmonize_prompt(measure_number, prompt)
        return f"Takt {measure_number} harmonisiert zu {chord_name}"
    except Exception as e:
        return f"Fehler: {str(e)}"

def undo():
    session.undo()
    return "Undo durchgeführt"

def redo():
    session.redo()
    return "Redo durchgeführt"

def export_score():
    from tempfile import NamedTemporaryFile
    tmp = NamedTemporaryFile(delete=False, suffix=".xml")
    write_musicxml(session.current_score, tmp.name)
    return tmp.name

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("# LLM-SATB Harmonizer")

    with gr.Row():
        score_file = gr.File(label="MusicXML Score laden")
        load_btn = gr.Button("Laden")
        load_status = gr.Textbox(label="Status")

    load_btn.click(load_score, inputs=score_file, outputs=[load_status, score_file])

    measure_number = gr.Number(label="Taktnummer", value=1)
    prompt = gr.Textbox(label="Prompt für Harmonisierung", value="Make measure 1 more romantic")
    harmonize_btn = gr.Button("Harmonisieren")
    harmonize_output = gr.Textbox(label="Ergebnis")

    harmonize_btn.click(harmonize_takt, inputs=[measure_number, prompt], outputs=harmonize_output)

    with gr.Row():
        undo_btn = gr.Button("Undo")
        redo_btn = gr.Button("Redo")
        export_btn = gr.Button("Export Score")
        export_file = gr.File(label="Exportierte Datei")

    undo_btn.click(undo, outputs=harmonize_output)
    redo_btn.click(redo, outputs=harmonize_output)
    export_btn.click(export_score, outputs=export_file)

demo.launch()
