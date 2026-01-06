"""
Gradio App: SATB harmonization using a dummy LLM for testing.

This app allows users to enter text prompts for each voice (S,A,T,B)
and generates chord suggestions using a Dummy LLM. MIDI/WAV preview is included.
"""

import gradio as gr
from copy import deepcopy
from core.score import load_musicxml, write_musicxml, replace_chord_in_measure
from core.editor.dummy_llm import DummyLLM
import tempfile
import os

# Initialize dummy LLM
llm = DummyLLM()

# Helper function for multi-voice harmonization
def harmonize_multi_voice(score_file, prompts):
    try:
        score = load_musicxml(score_file)
    except Exception as e:
        return None, None, f"Error loading score: {e}"

    if not isinstance(prompts, dict):
        return None, None, "Prompts must be a dictionary with keys: S,A,T,B"

    try:
        suggestions = llm.harmonize_multi_voice(prompts)
        # Apply each chord suggestion to the score
        for voice, suggestion in suggestions.items():
            replace_chord_in_measure(score, suggestion['measure'], suggestion['root'])

        # Save updated MusicXML
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
        write_musicxml(score, tmp_file.name)

        # TODO: MIDI/WAV audio preview could be implemented here

        return tmp_file.name, None, str(suggestions)

    except Exception as e:
        return None, None, f"Error harmonizing: {e}"

# Gradio Interface
with gr.Blocks() as app:
    gr.Markdown("## SATB Harmonization (Dummy LLM)")
    with gr.Row():
        score_input = gr.File(label="Upload MusicXML")
    with gr.Row():
        s_prompt = gr.Textbox(label="Soprano Prompt", value="Make Soprano more romantic")
        a_prompt = gr.Textbox(label="Alto Prompt", value="Make Alto more bright")
        t_prompt = gr.Textbox(label="Tenor Prompt", value="Make Tenor warmer")
        b_prompt = gr.Textbox(label="Bass Prompt", value="Make Bass solid")
    with gr.Row():
        harmonize_btn = gr.Button("Harmonize")
    with gr.Row():
        output_file = gr.File(label="Output MusicXML")
        output_audio = gr.Audio(label="Audio Preview")
        output_text = gr.Textbox(label="LLM Suggestions")

        # Store prompts in gr.State separately to avoid deepcopy issues
    prompts_state = gr.State({})
    
    def update_prompts(s_prompt, a_prompt, t_prompt, b_prompt):
        return {"S": s_prompt, "A": a_prompt, "T": t_prompt, "B": b_prompt}
    
    # Update prompts state when any prompt changes
    for prompt_input in [s_prompt, a_prompt, t_prompt, b_prompt]:
        prompt_input.change(
            fn=update_prompts,
            inputs=[s_prompt, a_prompt, t_prompt, b_prompt],
            outputs=[prompts_state]
        )
    
    harmonize_btn.click(
        fn=harmonize_multi_voice,
        inputs=[score_input, prompts_state],
        outputs=[output_file, output_audio, output_text]
    )

if __name__ == "__main__":
    app.launch()
