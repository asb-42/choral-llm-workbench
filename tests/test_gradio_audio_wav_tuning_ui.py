# File: tests/test_gradio_audio_wav_tuning_ui.py

import tempfile
from pathlib import Path
from core.audio import generate_test_midi, midi_to_wav
from core.config import Config

def test_gradio_audio_tuning():
    config = Config()
    default_tuning = config.get("base_tuning", 432)
    print(f"Default base tuning from config: {default_tuning} Hz")

    # Temporäre MIDI-Datei erzeugen
    midi_path = Path(tempfile.mktemp(suffix=".mid"))
    generate_test_midi(str(midi_path))
    print(f"MIDI file generated: {midi_path}")

    # Test für alle Base-Tunings
    for tuning in [432, 440, 443]:
        wav_path = Path(tempfile.mktemp(suffix=f"_{tuning}Hz.wav"))
        print(f"Rendering WAV at {tuning} Hz...")
        try:
            midi_to_wav(str(midi_path), str(wav_path), base_tuning=tuning)
            print(f"WAV file generated: {wav_path}")
        except Exception as e:
            print(f"Error rendering WAV at {tuning} Hz: {e}")

if __name__ == "__main__":
    test_gradio_audio_tuning()
