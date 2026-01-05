import os
import gradio as gr
from core.editor.session import Session
from core.audio import render_audio_with_tuning
from core.score import load_musicxml
from core.editor.dummy_llm import DummyLLM

# Initialize session and LLM
session = Session()
llm = DummyLLM()

def harmonize_multi_voice(s_prompt: str, a_prompt: str, t_prompt: str, b_prompt: str, base_tuning=432.0):
    """
    Harmonize prompts for S, A, T, B voices and render WAV files.
    """
    if session.current_score is None:
        return None, None, "No score loaded."

    try:
        # Harmonize each voice
        s_result = llm.harmonize_prompt(s_prompt, voice="S")
        a_result = llm.harmonize_prompt(a_prompt, voice="A")
        t_result = llm.harmonize_prompt(t_prompt, voice="T")
        b_result = llm.harmonize_prompt(b_prompt, voice="B")

        results = {
            "S": s_result,
            "A": a_result,
            "T": t_result,
            "B": b_result
        }

        # Export MIDI
        midi_path = "/tmp/session_output.mid"
        session.current_score.write("midi", fp=midi_path)

        # Render WAV with selected base tuning
        wav_path = f"/tmp/session_output_{int(base_tuning)}Hz.wav"
        render_audio_with_tuning(
            midi_path=midi_path,
            wav_path=wav_path,
            base_tuning=base_tuning
        )

        return midi_path, wav_path, str(results)

    except Exception as e:
        return None, None, f"Error harmonizing or rendering WAV: {e}"

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("### Choral LLM Harmonizer + Audio Preview")
    s_input = gr.Textbox(label="Soprano Prompt")
    a_input = gr.Textbox(label="Alto Prompt")
    t_input = gr.Textbox(label="Tenor Prompt")
    b_input = gr.Textbox(label="Bass Prompt")
    tuning_input = gr.Slider(label="Base Tuning (Hz)", minimum=432, maximum=443, step=1, value=432)

    midi_output = gr.File(label="MIDI Output")
    wav_output = gr.File(label="WAV Output")
    result_output = gr.Textbox(label="Harmonization Results")

    run_button = gr.Button("Harmonize & Render WAV")
    run_button.click(
        harmonize_multi_voice,
        inputs=[s_input, a_input, t_input, b_input, tuning_input],
        outputs=[midi_output, wav_output, result_output]
    )

if __name__ == "__main__":
    demo.launch()
