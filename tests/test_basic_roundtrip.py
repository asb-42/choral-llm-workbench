import os
import tempfile
from musicxml_parser import MusicXMLParser
from tlr_converter import TLRConverter
from tlr_parser import TLRParser
from musicxml_exporter import MusicXMLExporter


def test_basic_roundtrip():
    """Test basic MusicXML → TLR → MusicXML roundtrip"""
    parser = MusicXMLParser()
    converter = TLRConverter()
    tlr_parser = TLRParser()
    exporter = MusicXMLExporter()
    
    # Create a simple test case
    input_file = None
    try:
        # Create a minimal test MusicXML content
        test_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1">
      <part-name>Music</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
        <key>
          <fifths>0</fifths>
        </key>
        <time>
          <beats>4</beats>
          <beat-type>4</beat-type>
        </time>
        <clef>
          <sign>G</sign>
          <line>2</line>
        </clef>
      </attributes>
      <note>
        <pitch>
          <step>C</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <type>quarter</type>
      </note>
    </measure>
  </part>
</score-partwise>'''
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(test_xml)
            input_file = f.name
        
        # Parse
        score = parser.parse_file(input_file)
        assert score is not None
        
        # Convert to TLR
        tlr_text = converter.score_to_tlr(score)
        assert len(tlr_text) > 0
        
        # Parse TLR back
        parsed_score = tlr_parser.parse_tlr(tlr_text)
        assert parsed_score is not None
        
        # Export back to MusicXML
        output_xml = exporter.export_to_musicxml(parsed_score)
        assert len(output_xml) > 0
        
        print("✅ Basic roundtrip test passed")
        
    finally:
        if input_file and os.path.exists(input_file):
            os.unlink(input_file)


if __name__ == "__main__":
    test_basic_roundtrip()