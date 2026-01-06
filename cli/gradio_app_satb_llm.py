"""
Gradio App: SATB harmonization using a modern LLM adapter (Ollama backend).

This app allows users to enter text prompts for each voice (S,A,T,B)
and generates chord suggestions using an Ollama-backed LLM adapter. MIDI/WAV preview is included.
"""

import gradio as gr
from core.score import load_musicxml, write_musicxml, replace_chord_in_measure
from core.llm.adapter import LLMAdapter
from core.llm.llm_wrapper import OllamaLLM
from core.score.llm import apply_llm_chords_to_measures
from core.audio import score_to_midi, render_audio_with_tuning, render_score_audio
from core.config import get_config
from core.i18n import _
from core.constants import AudioDefaults
import tempfile
import os
from pathlib import Path

# Initialize LLM via config (default Ollama via adapter)
config = get_config()
llm = LLMAdapter(model_name=getattr(config.llm, 'model_name', 'mistral-7b'))

# Helper function for multi-voice harmonization
def harmonize_multi_voice(score_file, prompts, base_tuning=None):
    """
    Harmonize a MusicXML file with voice-specific prompts and audio preview.
    """
    try:
        score = load_musicxml(score_file)
    except Exception as e:
        return None, None, f"Error loading score: {e}"

    if not isinstance(prompts, dict):
        return None, None, "Prompts must be a dictionary with keys: S,A,T,B"

    # Use default tuning if not provided
    if base_tuning is None:
        base_tuning = AudioDefaults.BASE_TUNING

    try:
        suggestions = llm.harmonize_multi_voice(prompts)
        score = apply_llm_chords_to_measures(score, suggestions)

        # Save updated MusicXML
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
        write_musicxml(score, tmp_file.name)

        # Generate audio preview with tuning
        try:
            audio_file = render_score_audio(score, base_tuning=base_tuning)
        except Exception as audio_error:
            print(f"Audio rendering failed: {audio_error}")
            audio_file = None

        # Convert to proper file paths for Gradio
        xml_path = Path(tmp_file.name)
        audio_path = Path(str(audio_file)) if audio_file else None
        
        return str(xml_path), str(audio_path), str(suggestions)

    except Exception as e:
        return None, None, f"Error harmonizing: {e}"


def update_tuning_display(tuning_value):
    """Update the tuning display."""
    return f"{tuning_value} Hz"

# Gradio Interface
with gr.Blocks() as app:
    gr.Markdown("## SATB Harmonization (LLM Adapter)")
    
    # File input
    with gr.Row():
        score_input = gr.File(label="Upload MusicXML")
    
    # Tuning controls
    with gr.Row():
        with gr.Column():
            tuning_slider = gr.Slider(
                minimum=min(AudioDefaults.TUNING_OPTIONS),
                maximum=max(AudioDefaults.TUNING_OPTIONS),
                value=AudioDefaults.BASE_TUNING,
                step=1.0,
                label="Base Tuning (Hz)"
            )
            tuning_display = gr.Textbox(label="Current Tuning", value=f"{AudioDefaults.BASE_TUNING} Hz", interactive=False)
    
    # Prompts
    with gr.Row():
        s_prompt = gr.Textbox(label="Soprano Prompt", value="Make Soprano more romantic")
        a_prompt = gr.Textbox(label="Alto Prompt", value="Make Alto more bright")
        t_prompt = gr.Textbox(label="Tenor Prompt", value="Make Tenor warmer")
        b_prompt = gr.Textbox(label="Bass Prompt", value="Make Bass solid")
    
    with gr.Row():
        harmonize_btn = gr.Button("Harmonize", variant="primary")
    
    with gr.Row():
        output_file = gr.File(label="Output MusicXML")
        output_audio = gr.Audio(label="Audio Preview")
        output_text = gr.Textbox(label="LLM Suggestions", lines=5)

    prompts_state = gr.State({})

    def update_prompts(s_prompt, a_prompt, t_prompt, b_prompt):
        return {"S": s_prompt, "A": a_prompt, "T": t_prompt, "B": b_prompt}

    tuning_slider.change(
        fn=update_tuning_display,
        inputs=[tuning_slider],
        outputs=[tuning_display]
    )

    for prompt_input in [s_prompt, a_prompt, t_prompt, b_prompt]:
        prompt_input.change(
            fn=update_prompts,
            inputs=[s_prompt, a_prompt, t_prompt, b_prompt],
            outputs=[prompts_state]
        )

    harmonize_btn.click(
        fn=harmonize_multi_voice,
        inputs=[score_input, prompts_state, tuning_slider],
        outputs=[output_file, output_audio, output_text]
    )

if __name__ == "__main__":
    app.launch()
