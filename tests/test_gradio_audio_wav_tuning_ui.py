import os
from core.audio import render_audio_with_tuning

def test_gradio_audio_tuning():
    # Beispiel-MusicXML
    musicxml_path = "tests/data/test_score.musicxml"
    if not os.path.exists(musicxml_path):
        print(f"MusicXML test file not found: {musicxml_path}")
        return

    base_tunings = [432.0, 440.0, 443.0]
    soundfont_path = os.path.expanduser("~/.fluidsynth/default_sound_font.sf2")

    for tuning in base_tunings:
        try:
            print(f"\nRendering WAV at {tuning} Hz using SoundFont {soundfont_path} ...")
            wav_path = render_audio_with_tuning(musicxml_path, base_tuning=tuning, soundfont_path=soundfont_path)
            print(f"WAV rendered at {tuning} Hz: {wav_path}")
        except Exception as e:
            print(f"Error rendering WAV at {tuning} Hz: {e}")

if __name__ == "__main__":
    test_gradio_audio_tuning()
