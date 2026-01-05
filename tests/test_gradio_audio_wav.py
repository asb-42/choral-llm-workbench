import tempfile
from core.score import load_musicxml
from cli.gradio_app_audio_wav import render_audio

def main():
    # Beispiel-MusicXML (minimal)
    test_xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <score-partwise version="3.1">
      <part-list>
        <score-part id="P1"><part-name>Piano</part-name></score-part>
      </part-list>
      <part id="P1">
        <measure number="1">
          <attributes>
            <divisions>1</divisions>
            <key><fifths>0</fifths></key>
            <time><beats>4</beats><beat-type>4</beat-type></time>
            <clef><sign>G</sign><line>2</line></clef>
          </attributes>
          <note>
            <pitch><step>C</step><octave>4</octave></pitch>
            <duration>1</duration>
            <type>quarter</type>
          </note>
        </measure>
      </part>
    </score-partwise>"""

    # Temporäre XML-Datei erstellen
    tmp_xml = tempfile.NamedTemporaryFile(suffix=".xml", delete=False)
    tmp_xml.write(test_xml_content.encode("utf-8"))
    tmp_xml.flush()

    # Dummy SoundFont (ersetze hier durch einen echten Pfad, falls vorhanden)
    tmp_sf2 = tempfile.NamedTemporaryFile(suffix=".sf2", delete=False)

    # Base Tuning testen
    midi_file, wav_file, status = render_audio(tmp_xml, tmp_sf2, "432")

    print("MIDI file:", midi_file)
    print("WAV file:", wav_file)
    print("Status:", status)

    if midi_file and wav_file:
        print("Test passed: MIDI and WAV successfully generated.")
    else:
        print("Test failed: Audio not generated.")

if __name__ == "__main__":
    main()
