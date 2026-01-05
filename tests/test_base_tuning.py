# tests/test_base_tuning.py

from pathlib import Path
from core.audio import midi_to_wav
from core.score import load_musicxml
from core.config import Config

def main():
    config = Config()
    print(f"Default base tuning from config: {config.audio_tuning_default} Hz")

    # Beispiel-MIDI generieren aus kurzer Dummy-Partitur
    score_path = Path("examples") / "test.xml"
    if not score_path.exists():
        print("No test MusicXML found, please provide one.")
        return

    score = load_musicxml(score_path)

    # Midi-Datei temporär speichern
    midi_path = Path("/tmp/test_audio.mid")
    score.write("midi", fp=midi_path)
    print(f"MIDI file generated: {midi_path}")

    # Teste alle Base-Tunings
    for tuning in [432, 440, 443]:
        wav_path = Path(f"/tmp/test_audio_{tuning}Hz.wav")
        try:
            print(f"Rendering WAV at {tuning} Hz...")
            midi_to_wav(midi_path, wav_path, tuning=tuning)
            if wav_path.exists():
                print(f"WAV file generated: {wav_path}")
            else:
                print(f"WAV file missing: {wav_path}")
        except Exception as e:
            print(f"Error rendering WAV at {tuning} Hz: {e}")

if __name__ == "__main__":
    main()
