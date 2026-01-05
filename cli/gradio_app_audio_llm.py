import os
import gradio as gr

from core.editor.session import Session
from core.score import load_musicxml
from core.audio import render_audio_with_tuning
from core.editor.dummy_llm import DummyLLM

# Global session + LLM
session = Session()
llm = DummyLLM()


# -------------------------------------------------
# Score loading
# -------------------------------------------------

def load_score_ui(musicxml_file):
    if musicxml_file is None:
        return "No file selected."

    try:
        score = load_musicxml(musicxml_file.name)
        session.load_score(score)
        return f"Score loaded: {os.path.basename(musicxml_file.name)}"
    except Exception as e:
        return f"Error loading score: {e}"


# -------------------------------------------------
# Harmonization + audio rendering
# -------------------------------------------------

def harmonize_multi_voice(
    s_prompt: str,
    a_prompt: str,
    t_prompt: str,
    b_prompt: str,
    base_tuning: float
):
    if session.current_score is None:
        return None, None, "No score loaded."

    try:
        # Dummy LLM – no voice kwarg, keep it simple
        results = {
            "S": llm.harmonize_prompt(s_prompt),
            "A": llm.harmonize_prompt(a_prompt),
            "T": llm.harmonize_prompt(t_prompt),
            "B": llm.harmonize_prompt(b_prompt),
        }

        # Export MIDI
        midi_path = "/tmp/choral_llm_output.mid"
        session.current_score.write("midi", fp=midi_path)

        # Render WAV
        wav_path = f"/tmp/choral_llm_output_{int(base_tuning)}Hz.wav"
        render_audio_with_tuning(
            midi_path=midi_path,
            wav_path=wav_path,
            base_tuning=base_tuning,
        )

        return midi_path, wav_path, str(results)

    except Exception as e:
        return None, None, f"Error harmonizing or rendering WAV: {e}"


# -------------------------------------------------
# Gradio UI
# -------------------------------------------------

with gr.Blocks() as demo:
    gr.Markdown("## Choral-LLM Audio Workbench")

    with gr.Box():
        gr.Markdown("### 1. Load score")
        score_file = gr.File(
            label="MusicXML score",
            file_types=[".musicxml", ".xml"]
        )
        load_btn = gr.Button("Load score")
        load_status = gr.Textbox(label="Status", interactive=False)

        load_btn.click(
            load_score_ui,
            inputs=score_file,
            outputs=load_status
        )

    with gr.Box():
        gr.Markdown("### 2. Harmonization prompts")
        s_input = gr.Textbox(label="Soprano prompt")
        a_input = gr.Textbox(label="Alto prompt")
        t_input = gr.Textbox(label="Tenor prompt")
        b_input = gr.Textbox(label="Bass prompt")

        tuning = gr.Slider(
            label="Base tuning (Hz)",
            minimum=432,
            maximum=443,
            step=1,
            value=432
        )

        run_btn = gr.Button("Harmonize & render audio")

        midi_out = gr.File(label="MIDI output")
        wav_out = gr.File(label="WAV output")
        result_out = gr.Textbox(label="LLM result")

        run_btn.click(
            harmonize_multi_voice,
            inputs=[s_input, a_input, t_input, b_input, tuning],
            outputs=[midi_out, wav_out, result_out]
        )


if __name__ == "__main__":
    demo.launch()
