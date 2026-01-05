# tests/test_gradio_audio_wav_tuning.py
import os
import tempfile
from core.audio import midi_to_wav
from core.score.parser import load_musicxml
from core.score.reharmonize import replace_chord_in_measure, make_chord

def test_base_tuning():
    # Test MusicXML
    musicxml_path = "examples/test.xml"
    score = load_musicxml(musicxml_path)
    print("Score loaded.")

    # Generate temporary MIDI file
    midi_fd, midi_path = tempfile.mkstemp(suffix=".mid")
    os.close(midi_fd)

    # Minimal MIDI generation: just add a simple chord for testing
    from mido import MidiFile, MidiTrack, Message
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    # Add a single C4 quarter note
    track.append(Message("note_on", note=60, velocity=64, time=0))
    track.append(Message("note_off", note=60, velocity=64, time=480))
    mid.save(midi_path)
    print(f"MIDI file generated: {midi_path}")

    # Test different base tunings
    for tuning in [432, 440, 443]:
        wav_fd, wav_path = tempfile.mkstemp(suffix=f"_{tuning}Hz.wav")
        os.close(wav_fd)
        try:
            midi_to_wav(midi_path, wav_path, base_tuning=tuning)
            print(f"WAV rendered at {tuning} Hz: {wav_path}")
            if not os.path.exists(wav_path):
                print(f"Error: WAV file not created for {tuning} Hz")
        except Exception as e:
            print(f"Error rendering WAV at {tuning} Hz: {e}")

    # Cleanup temporary MIDI file
    os.remove(midi_path)
    print("Test completed.")

if __name__ == "__main__":
    test_base_tuning()
