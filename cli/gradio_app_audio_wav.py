import gradio as gr
import tempfile
from core.score import load_musicxml
from core.audio import midi_to_wav
from music21 import converter

def render_audio(xml_file, soundfont_path, base_tuning):
    try:
        # Score laden
        score = load_musicxml(xml_file.name)
        
        # Temporäre Dateien für MIDI/WAV
        tmp_midi = tempfile.NamedTemporaryFile(suffix=".mid", delete=False)
        tmp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        
        # Score als MIDI schreiben
        score.write("midi", fp=tmp_midi.name)
        
        # MIDI in WAV konvertieren
        midi_to_wav(tmp_midi.name, tmp_wav.name,
                    soundfont_path=soundfont_path,
                    base_tuning=float(base_tuning))
        
        return tmp_midi.name, tmp_wav.name, "Audio rendering completed!"
    
    except Exception as e:
        return None, None, f"Error rendering audio: {e}"

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("## Choral Workbench: Audio Preview (MIDI → WAV)")

    with gr.Row():
        xml_input = gr.File(label="MusicXML File", file_types=[".xml"])
        soundfont_input = gr.File(label="SoundFont (.sf2)", file_types=[".sf2"])
        base_tuning_input = gr.Dropdown(label="Base Tuning (Hz)",
                                        choices=["432", "440", "443"],
                                        value="432")

    with gr.Row():
        midi_output = gr.File(label="MIDI Output")
        wav_output = gr.Audio(label="WAV Output")
        status_output = gr.Textbox(label="Status")

    render_btn = gr.Button("Render Audio")
    render_btn.click(render_audio,
                     inputs=[xml_input, soundfont_input, base_tuning_input],
                     outputs=[midi_output, wav_output, status_output])

if __name__ == "__main__":
    demo.launch()
