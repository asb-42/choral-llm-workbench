import gradio as gr
from core.score import load_musicxml, write_musicxml, apply_llm_chords_to_measures
from llm.ollama_adapter import OllamaAdapter
import tempfile
from midi2audio import FluidSynth

def reharmonize_satb_llm(xml_file, measure_numbers, prompt):
    """
    Multi-Measure SATB Reharmonization mit LLM.
    :prompt: freie Beschreibung, z.B. "Make measure 1-2 more romantic"
    """
    score = load_musicxml(xml_file.name)
    llm = OllamaAdapter()

    # Measures parsen
    measures = [int(x.strip()) for x in measure_numbers.split(',')]

    # LLM Vorschläge
    chords_per_voice = llm.generate_harmony(prompt, context={})

    # Core anwenden
    apply_llm_chords_to_measures(score, measures, chords_per_voice)

    # Temporäre MusicXML-Datei
    tmp_xml = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
    write_musicxml(score, tmp_xml.name)

    # MIDI → WAV
    tmp_midi = tempfile.NamedTemporaryFile(delete=False, suffix=".midi")
    score.write('midi', fp=tmp_midi.name)
    tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    fs = FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2")
    fs.midi_to_audio(tmp_midi.name, tmp_wav.name)

    return tmp_xml.name, tmp_wav.name, f"Applied LLM chords for measures {measures}"

# Gradio Interface
iface = gr.Interface(
    fn=reharmonize_satb_llm,
    inputs=[
        gr.File(label="MusicXML Input"),
        gr.Textbox(label="Measures (comma-separated)", value="1"),
        gr.Textbox(label="Prompt (LLM)", placeholder="Make measure 1-2 more romantic")
    ],
    outputs=[
        gr.File(label="Modified MusicXML Output"),
        gr.Audio(label="Audio Preview"),
        gr.Textbox(label="Status")
    ],
    title="Choral LLM Workbench: SATB Multi-Measure with LLM",
    description="Reharmonize multiple measures for SATB voices using LLM-generated chords and preview audio"
)

if __name__ == "__main__":
    iface.launch()
