import gradio as gr
from core.score import load_musicxml, write_musicxml, update_single_measure
import tempfile
from midi2audio import FluidSynth

def edit_single_measure(xml_file, measure_number, s_chord, a_chord, t_chord, b_chord):
    score = load_musicxml(xml_file.name)
    
    chords_per_voice = {
        "S": s_chord,
        "A": a_chord,
        "T": t_chord,
        "B": b_chord
    }

    # Takt aktualisieren
    update_single_measure(score, int(measure_number), chords_per_voice)

    # MusicXML temporär
    tmp_xml = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
    write_musicxml(score, tmp_xml.name)

    # MIDI → WAV
    tmp_midi = tempfile.NamedTemporaryFile(delete=False, suffix=".midi")
    score.write('midi', fp=tmp_midi.name)
    tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    fs = FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2")
    fs.midi_to_audio(tmp_midi.name, tmp_wav.name)

    return tmp_xml.name, tmp_wav.name, f"Updated measure {measure_number}"

# Gradio Interface
iface = gr.Interface(
    fn=edit_single_measure,
    inputs=[
        gr.File(label="MusicXML Input"),
        gr.Textbox(label="Measure Number", value="1"),
        gr.Textbox(label="Soprano Chord", value="Cmaj"),
        gr.Textbox(label="Alto Chord", value="G"),
        gr.Textbox(label="Tenor Chord", value="E"),
        gr.Textbox(label="Bass Chord", value="C")
    ],
    outputs=[
        gr.File(label="Modified MusicXML Output"),
        gr.Audio(label="Audio Preview"),
        gr.Textbox(label="Status")
    ],
    title="Choral LLM Workbench: SATB Single-Measure Editor",
    description="Edit a single measure's chords for SATB voices and preview audio instantly"
)

if __name__ == "__main__":
    iface.launch()
