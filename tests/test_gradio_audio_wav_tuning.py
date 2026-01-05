# tests/test_gradio_audio_wav_tuning.py

import os
from tempfile import NamedTemporaryFile
from core.audio import midi_to_wav
from core.score import load_musicxml
from core.config import Config

def main():
    # Beispiel-Score laden
    score_path = "examples/test.xml"
    try:
        score = load_musicxml(score_path)
        print("Score loaded.")
    except Exception as e:
        print(f"Error loading score: {e}")
        return

    # MIDI-Datei erzeugen
    with NamedTemporaryFile(suffix=".mid", delete=False) as tmp_midi:
        midi_path = tmp_midi.name
    try:
        score.write("midi", fp=midi_path)
        print(f"MIDI file generated: {midi_path}")
    except Exception as e:
        print(f"Error writing MIDI: {e}")
        return

    # Alle Base-Tuning-Werte durchtesten
    for tuning in [432, 440, 443]:
        with NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            wav_path = tmp_wav.name
        print(f"Rendering WAV at {tuning} Hz...")

        try:
            midi_to_wav(midi_path, wav_path, base_tuning=tuning)
            print(f"WAV file generated: {wav_path}")
        except Exception as e:
            print(f"Error rendering WAV at {tuning} Hz: {e}")

if __name__ == "__main__":
    main()
