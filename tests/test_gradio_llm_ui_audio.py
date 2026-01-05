# File: tests/test_gradio_llm_ui_audio.py

import gradio as gr
from cli.gradio_app_llm_models import select_model, harmonize_voices
from core.audio import midi_to_wav
from core.score.parser import write_musicxml
import tempfile
import os

def run_gradio_audio_test():
    # Dummy-LLM auswählen
    select_model("Dummy")

    def harmonize_interface(s_prompt, a_prompt, t_prompt, b_prompt):
        prompts = {
            "S": s_prompt,
            "A": a_prompt,
            "T": t_prompt,
            "B": b_prompt
        }

        # Harmonisierung aufrufen
        results, status = harmonize_voices(prompts)

        # Dummy: generiertes MIDI aus SATB-Chords erstellen
        midi_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mid").name
        wav_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name

        # Hier einfach ein leeres MIDI für Demo
        # In echter Implementierung wird MIDI aus current_score erzeugt
        with open(midi_file, "wb") as f:
            f.write(b"MThd\x00\x00\x00\x06\x00\x01\x00\x04\x00\x60MTrk\x00\x00\x00\x04\x00\xFF\x2F\x00")

        # WAV-Rendering (Default Base Tuning aus config)
        try:
            midi_to_wav(midi_file, wav_file)
            audio_preview = wav_file
        except Exception as e:
            audio_preview = None
            status += f"\nError rendering WAV: {e}"

        return str(results), status, audio_preview

    # Gradio Interface
    with gr.Blocks() as demo:
        gr.Markdown("### SATB Harmonization Test with Audio Preview (Dummy LLM)")

        s_input = gr.Textbox(label="Soprano prompt", value="Make soprano lyrical")
        a_input = gr.Textbox(label="Alto prompt", value="Smooth alto line")
        t_input = gr.Textbox(label="Tenor prompt", value="Add warmth to tenor")
        b_input = gr.Textbox(label="Bass prompt", value="Strengthen bass foundation")

        output_text = gr.Textbox(label="Harmonization Results")
        status_text = gr.Textbox(label="Status")
        audio_output = gr.Audio(label="Audio Preview", type="filepath")

        run_btn = gr.Button("Harmonize & Render Audio")
        run_btn.click(
            harmonize_interface,
            inputs=[s_input, a_input, t_input, b_input],
            outputs=[output_text, status_text, audio_output]
        )

    demo.launch(share=False)

if __name__ == "__main__":
    run_gradio_audio_test()
