import gradio as gr
from core.score import load_musicxml, write_musicxml, replace_chord_in_measure
from llm.ollama_adapter import OllamaAdapter
import tempfile
import music21
import pygame
import time

def reharmonize_with_audio(xml_file, measure_number, prompt):
    # Datei laden
    score = load_musicxml(xml_file.name)

    # LLM-Adapter (Stub)
    llm = OllamaAdapter()
    suggestion = llm.generate_harmony(prompt, context={})

    # MVP: letzte Wort als Root
    # root_note = prompt.strip().split()[-1]
    valid_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    root_note = None
    for w in prompt.strip().split():
        if w.upper() in valid_notes:
            root_note = w.upper()
            break

    if root_note is None:
        return None, "Error: No valid root note found in prompt (use C, D#, F, etc.)"

    # Takt ersetzen
    replace_chord_in_measure(score, measure_number, root_note)

    # Temporäre MusicXML-Ausgabe
    tmp_xml = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
    write_musicxml(score, tmp_xml.name)

    # MIDI erzeugen
    tmp_midi = tempfile.NamedTemporaryFile(delete=False, suffix=".midi")
    score.write('midi', fp=tmp_midi.name)

    # Audio abspielen mit pygame
    pygame.mixer.init()
    pygame.mixer.music.load(tmp_midi.name)
    pygame.mixer.music.play()
    # Warten, bis Musik endet
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.quit()

    return tmp_xml.name, f"Applied LLM suggestion: '{root_note}' and played audio"

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
        gr.Textbox(label="Status")
    ],
    title="Choral LLM Workbench MVP with Audio Preview",
    description="Reharmonize a measure and play audio preview (MIDI)."
)

if __name__ == "__main__":
    iface.launch()
