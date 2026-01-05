# tests/test_gradio_audio_wav.py

import os
import tempfile
from core.score import load_musicxml
from core.audio import midi_to_wav, DEFAULT_SOUNDFONT_PATH
from core.score.reharmonize import write_midi

def main():
    # Test-Score laden
    score_path = "tests/data/test_score.musicxml"  # Pfad zu einer Beispiel-MusicXML
    if not os.path.exists(score_path):
        print(f"Test score not found: {score_path}")
        return

    score = load_musicxml(score_path)
    print("Score loaded.")

    # MIDI-Datei temporär erzeugen
    with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tmp_midi:
        midi_path = tmp_midi.name
    write_midi(score, midi_path)
    print(f"MIDI file generated: {midi_path}")

    if not os.path.exists(DEFAULT_SOUNDFONT_PATH):
        print(f"Default SoundFont not found: {DEFAULT_SOUNDFONT_PATH}")
        print("Please download a GM SoundFont (e.g., FluidR3_GM.sf2) into your home directory as .fluidsynth/default_sound_font.sf2")
        return

    # WAV-Dateien für verschiedene Tunings rendern
    for tuning in [432.0, 440.0, 443.0]:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            wav_path = tmp_wav.name
        print(f"\nRendering WAV at {tuning}Hz...")
        try:
            midi_to_wav(midi_path, wav_path, base_tuning=tuning)
            print(f"WAV file generated: {wav_path}")
        except Exception as e:
            print(f"Error rendering WAV at {tuning}Hz: {e}")

if __name__ == "__main__":
    main()
