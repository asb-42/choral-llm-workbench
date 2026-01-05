import gradio as gr
import tempfile
from core.audio import midi_to_wav
from core.score.parser import load_musicxml
from core.config import Config

config = Config()

def render_audio_with_tuning(musicxml_path: str, base_tuning: float):
    try:
        # Score laden
        score = load_musicxml(musicxml_path)

        # Temporäre MIDI-Datei erzeugen
        midi_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mid").name
        score.write("midi", fp=midi_path)
        print(f"MIDI file generated: {midi_path}")

        # WAV-Datei erzeugen
        wav_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        print(f"Rendering WAV at {base_tuning} Hz using SoundFont {config.default_soundfont} ...")
        midi_to_wav(midi_path, wav_path, base_tuning=base_tuning)
        return wav_path
    except Exception as e:
        return f"Error rendering WAV: {e}"

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## Choral LLM Workbench - Audio Preview with Base Tuning")
    
    musicxml_input = gr.File(label="MusicXML File", file_types=[".xml", ".musicxml"])
    tuning_input = gr.Dropdown(
        label="Base Tuning (Hz)",
        choices=[432, 440, 443],
        value=config.base_tuning
    )
    audio_output = gr.Audio(label="WAV Preview", type="filepath")
    render_btn = gr.Button("Render Audio")

    render_btn.click(
        fn=render_audio_with_tuning,
        inputs=[musicxml_input, tuning_input],
        outputs=[audio_output]
    )

if __name__ == "__main__":
    demo.launch()
