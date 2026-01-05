# File: cli/gradio_app_audio_preview.py

import gradio as gr
from pathlib import Path
import tempfile
from core.audio import generate_test_midi, midi_to_wav
from core.config import Config

# Base-Tuning aus Config
config = Config()
DEFAULT_TUNING = config.get("base_tuning", 432)

def render_audio(base_tuning: int):
    """Erzeugt Test-MIDI, rendert WAV und gibt Pfad zurück"""
    # Temporäre MIDI-Datei
    tmp_midi = Path(tempfile.mktemp(suffix=".mid"))
    generate_test_midi(str(tmp_midi))
    
    # Temporäre WAV-Datei
    tmp_wav = Path(tempfile.mktemp(suffix=f"_{base_tuning}Hz.wav"))
    
    try:
        midi_to_wav(str(tmp_midi), str(tmp_wav), base_tuning=base_tuning)
        return str(tmp_wav)
    except Exception as e:
        return f"Error rendering audio: {e}"

with gr.Blocks(title="Choral LLM Audio Preview") as demo:
    gr.Markdown("### Audio Preview with Base Tuning Selection")
    
    tuning = gr.Radio(
        choices=[432, 440, 443],
        value=DEFAULT_TUNING,
        label="Select Base Tuning (Hz)"
    )
    
    output_audio = gr.Audio(label="Rendered Audio", type="filepath")
    
    render_button = gr.Button("Render WAV")
    render_button.click(render_audio, inputs=[tuning], outputs=[output_audio])

if __name__ == "__main__":
    demo.launch()
