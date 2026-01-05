# cli/gradio_app_audio_wav.py

import gradio as gr
from tempfile import NamedTemporaryFile
from core.audio import midi_to_wav
from core.score import load_musicxml
from core.config import Config

def render_audio(score_path, tuning_choice):
    try:
        score = load_musicxml(score_path)
    except Exception as e:
        return None, None, f"Error loading score: {e}"

    # Temporäre MIDI-Datei
    with NamedTemporaryFile(suffix=".mid", delete=False) as tmp_midi:
        midi_path = tmp_midi.name
    try:
        score.write("midi", fp=midi_path)
    except Exception as e:
        return None, None, f"Error writing MIDI: {e}"

    # Temporäre WAV-Datei
    with NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        wav_path = tmp_wav.name
    try:
        midi_to_wav(midi_path, wav_path, base_tuning=tuning_choice)
    except Exception as e:
        return midi_path, None, f"Error rendering WAV: {e}"

    return midi_path, wav_path, f"Rendered WAV at {tuning_choice} Hz"

def main():
    with gr.Blocks() as demo:
        gr.Markdown("### Choral LLM Audio Preview with Base Tuning")

        score_input = gr.File(label="Upload MusicXML Score")
        tuning_input = gr.Dropdown(label="Base Tuning (Hz)",
                                   choices=[432, 440, 443],
                                   value=Config.audio_tuning_default)
        output_midi = gr.File(label="Generated MIDI")
        output_wav = gr.Audio(label="Generated WAV")
        output_msg = gr.Textbox(label="Status")

        score_input.change(render_audio,
                           inputs=[score_input, tuning_input],
                           outputs=[output_midi, output_wav, output_msg])

    demo.launch()

if __name__ == "__main__":
    main()
