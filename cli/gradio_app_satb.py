import gradio as gr
from core.score import load_musicxml, write_musicxml, replace_chords_in_measures
from llm.ollama_adapter import OllamaAdapter
import tempfile
from midi2audio import FluidSynth

def reharmonize_satb(xml_file, measure_numbers, prompts_per_voice):
    """
    :measure_numbers: string, z.B. "1,2,3"
    :prompts_per_voice: dict {'S': "C D E", 'A': "G A B", 'T': "E F G", 'B': "C D E"}
    """
    score = load_musicxml(xml_file.name)
    llm = OllamaAdapter()
    
    # Parse measure numbers
    measures = [int(x.strip()) for x in measure_numbers.split(',')]
    
    # LLM -> extract root notes per voice
    roots_per_voice = {}
    valid_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    for voice, prompt in prompts_per_voice.items():
        words = prompt.strip().split()
        roots = []
        for m_idx in range(len(measures)):
            root = None
            for w in words:
                if w.upper() in valid_notes:
                    root = w.upper()
                    break
            if root is None:
                root = "C"  # Default fallback
            roots.append(root)
        roots_per_voice[voice] = roots

    # Core: Takte und Stimmen ersetzen
    replace_chords_in_measures(score, measures, roots_per_voice)

    # MusicXML temporär
    tmp_xml = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
    write_musicxml(score, tmp_xml.name)

    # MIDI -> WAV
    tmp_midi = tempfile.NamedTemporaryFile(delete=False, suffix=".midi")
    score.write('midi', fp=tmp_midi.name)
    tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    fs = FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2")
    fs.midi_to_audio(tmp_midi.name, tmp_wav.name)

    return tmp_xml.name, tmp_wav.name, f"Applied SATB reharmonization for measures {measures}"

# Gradio Interface
iface = gr.Interface(
    fn=reharmonize_satb,
    inputs=[
        gr.File(label="MusicXML Input"),
        gr.Textbox(label="Measures (comma-separated)", value="1"),
        gr.Label(label="Prompts per Voice", value={"S":"C","A":"G","T":"E","B":"C"})
    ],
    outputs=[
        gr.File(label="Modified MusicXML Output"),
        gr.Audio(label="Audio Preview"),
        gr.Textbox(label="Status")
    ],
    title="Choral LLM Workbench MVP: SATB Multi-Measure",
    description="Reharmonize multiple measures for SATB voices and preview audio"
)

if __name__ == "__main__":
    iface.launch()
