# Datei: cli/gradio_app_satb_llm.py

import gradio as gr
from copy import deepcopy
from core.score import load_musicxml, write_musicxml, apply_llm_chords_to_measures
from core.editor.dummy_llm import DummyLLM
from core.audio.audio import score_to_midi, midi_to_wav

# Dummy-LLM für Testzwecke
llm = DummyLLM()

def harmonize_multi_voice(score_file, prompts_per_voice):
    """
    Harmonisiert SATB Score nach Multi-Prompt Eingaben
    score_file: hochgeladene MusicXML-Datei
    prompts_per_voice: Dict {"S": prompt, "A": prompt, ...}
    """
    if not score_file:
        return None, None, "Keine Score-Datei hochgeladen."
    
    try:
        score = load_musicxml(score_file.name)
    except Exception as e:
        return None, None, f"Fehler beim Laden der Score: {e}"
    
    # Sicherstellen, dass prompts_per_voice ein Dict ist
    if isinstance(prompts_per_voice, str):
        # Gradio sendet manchmal Strings, z.B. JSON; wir versuchen zu evaluieren
        import ast
        try:
            prompts_per_voice = ast.literal_eval(prompts_per_voice)
        except Exception as e:
            return None, None, f"Prompts konnten nicht geparst werden: {e}"

    harmonized_info = {}
    
    # Für jede Stimme anwenden
    for voice, prompt in prompts_per_voice.items():
        try:
            chord_info = llm.harmonize_prompt(score, voice, prompt)
            harmonized_info[voice] = chord_info
        except Exception as e:
            return None, None, f"Fehler harmonizing {voice}: {e}"

    # Anwenden auf Score
    try:
        apply_llm_chords_to_measures(score, harmonized_info)
    except Exception as e:
        return None, None, f"Fehler beim Anwenden der Harmonisierung: {e}"

    # MIDI und WAV erzeugen
    try:
        midi_file = score_to_midi(score)
    except Exception as e:
        return None, None, f"Fehler beim Erstellen der MIDI-Datei: {e}"

    try:
        wav_file = midi_to_wav(midi_file)
    except Exception as e:
        wav_file = None  # WAV optional
        warning = f"Audio-Rendering Fehler: {e}"
    else:
        warning = "Harmonisierung erfolgreich"

    return midi_file, wav_file, warning


# Gradio Interface
with gr.Blocks() as app:
    gr.Markdown("# SATB Multi-Prompt Harmonizer (LLM Dummy)")

    with gr.Row():
        score_input = gr.File(label="MusicXML Datei hochladen", file_types=[".xml", ".mxl"])
        prompts_input = gr.Textbox(
            label="Prompts per Voice (Dict: {'S':'Cmaj', 'A':'Gmaj', ...})",
            value="{'S':'C major', 'A':'G major', 'T':'E minor', 'B':'C major'}",
            lines=2
        )

    with gr.Row():
        midi_out = gr.File(label="MIDI Output")
        wav_out = gr.Audio(label="WAV Audio Output")
        status_box = gr.Textbox(label="Status", interactive=False)

    harmonize_btn = gr.Button("Harmonize Multi-Voice")
    harmonize_btn.click(
        fn=harmonize_multi_voice,
        inputs=[score_input, prompts_input],
        outputs=[midi_out, wav_out, status_box]
    )

if __name__ == "__main__":
    app.launch()
