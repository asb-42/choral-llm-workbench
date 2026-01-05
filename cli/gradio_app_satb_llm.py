# Datei: cli/gradio_app_satb_llm.py

import gradio as gr
import json
import tempfile
import subprocess
from copy import deepcopy

from core.editor.session import EditorSession
from core.score.parser import load_musicxml, write_musicxml
from core.score.reharmonize import replace_chord_in_measure

# -------------------------
# Dummy LLM Definition
# -------------------------
class DummyLLM:
    """Dummy LLM für Testzwecke: gibt pro Prompt ein Measure und Root zurück"""
    def harmonize_prompt(self, prompt_text):
        # Einfacher Test: Measure 1, Root aus erstem Buchstaben des Prompts
        root_map = {"C":"C", "D":"D", "E":"E", "F":"F", "G":"G", "A":"A", "B":"B"}
        root = prompt_text[0].upper()
        if root not in root_map:
            root = "C"
        return {"measure": 1, "root": root, "quality": "major"}

# -------------------------
# Audio Rendering
# -------------------------
def render_midi_to_wav(score, soundfont_path="/usr/share/sounds/sf2/FluidR3_GM.sf2"):
    """
    Konvertiert music21.Score in WAV-Datei mittels FluidSynth.
    """
    from music21 import midi

    # temporäre MIDI-Datei
    with tempfile.NamedTemporaryFile(suffix=".midi", delete=False) as tmp_midi:
        mf = midi.translate.streamToMidiFile(score)
        mf.open(tmp_midi.name, 'wb')
        mf.write()
        mf.close()
        midi_file_path = tmp_midi.name

    # temporäre WAV-Datei
    tmp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wav_file_path = tmp_wav.name
    tmp_wav.close()

    # FluidSynth aufrufen
    subprocess.run([
        "fluidsynth", "-ni", soundfont_path, midi_file_path, "-F", wav_file_path, "-r", "44100"
    ], check=True)

    return wav_file_path

# -------------------------
# Session und LLM
# -------------------------
llm = DummyLLM()
session = EditorSession()

# -------------------------
# Harmonize Multi-Voice Funktion
# -------------------------
def harmonize_multi_voice(file, prompts_json):
    try:
        score = load_musicxml(file)
        session.load_score(score)
    except Exception as e:
        return None, None, f"Fehler beim Laden der Datei: {e}"

    try:
        prompts = json.loads(prompts_json)
    except Exception as e:
        return None, None, f"Fehler beim Parsen der Prompts: {e}"

    log = []
    for voice, prompt in prompts.items():
        change = llm.harmonize_prompt(prompt)
        try:
            replace_chord_in_measure(session.current_score, change["measure"], change["root"])
            log.append(f"{voice}: measure {change['measure']} -> {change['root']} {change['quality']}")
        except Exception as e:
            log.append(f"{voice}: Fehler beim Ersetzen der Akkorde: {e}")

    # temporäre MusicXML-Datei
    tmp_score = tempfile.NamedTemporaryFile(suffix=".xml", delete=False)
    write_musicxml(session.current_score, tmp_score.name)

    # WAV Rendering
    try:
        wav_file = render_midi_to_wav(session.current_score)
    except Exception as e:
        wav_file = None
        log.append(f"Audio Rendering fehlgeschlagen: {e}")

    return tmp_score.name, wav_file, "\n".join(log)

# -------------------------
# Gradio Interface
# -------------------------
with gr.Blocks() as app:
    gr.Markdown("### SATB Harmonizer with Audio Preview (Dummy LLM)")

    file_input = gr.File(label="MusicXML File", file_types=[".xml"])
    prompts_input = gr.Textbox(
        label="Voice Prompts JSON",
        value=json.dumps({"S": "bright", "A": "passing", "T": "romantic", "B": "stable"})
    )
    score_output = gr.File(label="Updated MusicXML")
    audio_output = gr.Audio(label="Preview WAV")
    log_output = gr.Textbox(label="Log")

    btn = gr.Button("Harmonize")
    btn.click(
        fn=harmonize_multi_voice,
        inputs=[file_input, prompts_input],
        outputs=[score_output, audio_output, log_output]
    )

if __name__ == "__main__":
    app.launch()
