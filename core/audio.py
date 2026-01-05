# Datei: core/audio.py

from music21 import midi
import subprocess

def midi_to_wav(score, wav_path, soundfont_path="/usr/share/sounds/sf2/FluidR3_GM.sf2"):
    """
    Render MIDI aus einem music21 Score zu WAV (über Fluidsynth).
    soundfont_path: Pfad zu SoundFont-Datei
    """
    # Temporäre MIDI-Datei
    tmp_midi = "/tmp/score_temp.mid"
    mf = midi.translate.streamToMidiFile(score)
    mf.open(tmp_midi, 'wb')
    mf.write()
    mf.close()

    # WAV mit Fluidsynth erzeugen
    cmd = [
        "fluidsynth",
        "-ni",
        soundfont_path,
        tmp_midi,
        "-F",
        wav_path,
        "-r",
        "44100"
    ]
    subprocess.run(cmd, check=True)
