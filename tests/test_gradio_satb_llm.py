# Datei: tests/test_gradio_satb_llm.py

import tempfile
import os
from core.score import load_musicxml
from cli.gradio_app_satb_llm import harmonize_multi_voice

def main():
    # Beispiel MusicXML-Datei (vorher erstellen oder eine kleine Testdatei nutzen)
    test_score_path = "examples/test.xml"
    if not os.path.exists(test_score_path):
        print(f"Test-Score nicht gefunden: {test_score_path}")
        return

    # Multi-Prompt Eingabe simulieren
    prompts = {
        "S": "Make melody brighter",
        "A": "Add tension",
        "T": "Support harmony",
        "B": "Reinforce bass"
    }

    # Öffnen der MusicXML-Datei als File-Objekt für harmonize_multi_voice
    with open(test_score_path, "rb") as f:
        midi_file, wav_file, status = harmonize_multi_voice(f, prompts)

    print("Status:", status)
    if midi_file:
        print("MIDI File:", midi_file)
        assert os.path.exists(midi_file), "MIDI-Datei wurde nicht erzeugt"
    else:
        print("Keine MIDI-Datei erzeugt.")

    if wav_file:
        print("WAV File:", wav_file)
        assert os.path.exists(wav_file), "WAV-Datei wurde nicht erzeugt"
    else:
        print("Keine WAV-Datei erzeugt.")

if __name__ == "__main__":
    main()
