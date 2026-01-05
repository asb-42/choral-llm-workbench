# File: tests/test_dummy_llm_preview.py

import os
from copy import deepcopy

from core.score.parser import load_musicxml, write_musicxml
from core.editor.dummy_llm import DummyLLM
from core.score.reharmonize import replace_chord_in_measure
from core.audio import midi_to_wav  # assumes core/audio.py exists with this function
from music21 import midi

def main():
    # Path to example MusicXML file
    xml_path = "examples/test.xml"
    
    if not os.path.exists(xml_path):
        print(f"Error: Example file not found at {xml_path}")
        return

    # Load the score
    score = load_musicxml(xml_path)
    print("Score loaded successfully.")

    # Initialize Dummy LLM
    llm = DummyLLM()

    # Define per-voice prompts
    prompts = {
        "S": "C major",
        "A": "G major",
        "T": "E minor",
        "B": "C major"
    }

    # Harmonize using Dummy LLM
    try:
        harmonization = llm.harmonize_multi_voice(prompts)
        print("Harmonization result from Dummy LLM:")
        for voice, chord_info in harmonization.items():
            print(f"  {voice}: measure {chord_info['measure']}, {chord_info['root']} {chord_info['quality']}")
    except Exception as e:
        print(f"Error during harmonization: {e}")
        return

    # Apply harmonization to a deepcopy of the score
    edited_score = deepcopy(score)
    for voice, chord_info in harmonization.items():
        measure = chord_info["measure"]
        root = chord_info["root"]
        quality = chord_info["quality"]
        try:
            replace_chord_in_measure(edited_score, measure, root, quality)
        except Exception as e:
            print(f"Error replacing chord for {voice} in measure {measure}: {e}")

    print("Dummy harmonization applied to score successfully.")

    # Export harmonized score to MusicXML
    output_xml_path = "tests/output_dummy_harmonization.xml"
    write_musicxml(edited_score, output_xml_path)
    print(f"Harmonized score written to {output_xml_path}")

    # Optional: Generate MIDI file
    output_midi_path = "tests/output_dummy_harmonization.mid"
    mf = midi.translate.music21ObjectToMidiFile(edited_score)
    mf.open(output_midi_path, 'wb')
    mf.write()
    mf.close()
    print(f"MIDI file written to {output_midi_path}")

    # Optional: Generate WAV from MIDI
    output_wav_path = "tests/output_dummy_harmonization.wav"
    if os.path.exists(output_midi_path):
        try:
            midi_to_wav(output_midi_path, output_wav_path)
            print(f"WAV audio rendered to {output_wav_path}")
        except Exception as e:
            print(f"Error rendering WAV: {e}")
    else:
        print("MIDI file not found, skipping WAV rendering.")

if __name__ == "__main__":
    main()
