import gradio as gr
from core.score import load_musicxml, write_musicxml, replace_chord_in_measure
from llm.ollama_adapter import OllamaAdapter
import tempfile
from midi2audio import FluidSynth
import os

def reharmonize_with_audio(xml_file, measure_number, prompt):
    # Datei laden
    score = load_musicxml(xml_file.name)

    # LLM-Adapter (Stub)
    llm = OllamaAdapter()
    suggestion = llm.generate_harmony(prompt, context={})

    # Prompt parsen
    valid_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    root_note = None
    for w in prompt.strip().split():
        if w.upper() in valid_notes:
            root_note = w.upper()
            break
    if root_note is None:
        return None, None, "Error: No valid root note found in prompt (use C, D#, F, etc.)"

    # Takt ersetzen
    replace_chord_in_measure(score, measure_number, root_note)

    # Temporäre MusicXML-Ausgabe
    tmp_xml = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
    write_musicxml(score, tmp_xml.name)

    # MIDI erzeugen
    tmp_midi = tempfile.NamedTemporaryFile(delete=False, suffix=".midi")
    score.write('midi', fp=tmp_midi.name)

    # WAV erzeugen mit SoundFont
    fs = FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2")  # SoundFont angeben
    tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    fs.midi_to_audio(tmp_midi.name, tmp_wav.name)

    return tmp_xml.name, tmp_wav.name, f"Applied LLM suggestion: '{root_note}'"

# Gradio Interface
iface = gr.Interface(
    fn=reharmonize_with_audio,
    inputs=[
        gr.File(label="MusicXML Input"),
        gr.Number(label="Measure Number", value=1),
        gr.Textbox(label="LLM Prompt", placeholder="e.g., Use C major")
    ],
    outputs=[
        gr.File(label="Modified MusicXML Output"),
        gr.Audio(label="Audio Preview"),   # WAV direkt abspielbar
        gr.Textbox(label="Status")
    ],
    title="Choral LLM Workbench MVP with Audio Preview (WAV)",
    description="Reharmonize a measure and play audio preview (MIDI → WAV)"
)

if __name__ == "__main__":
    iface.launch()
