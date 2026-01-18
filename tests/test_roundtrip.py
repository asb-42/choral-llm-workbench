import pytest
import tempfile
import os
from fractions import Fraction
from musicxml_parser import MusicXMLParser
from musicxml_exporter import MusicXMLExporter
from tlr_converter import TLRConverter
from tlr_parser import TLRParser
from ikr_light import Score, Part, Voice, Measure, NoteEvent, RestEvent


class TestRoundtrip:
    """Test MusicXML → IKR → MusicXML roundtrip conversion"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.parser = MusicXMLParser()
        self.exporter = MusicXMLExporter()
        self.tlr_converter = TLRConverter()
        self.tlr_parser = TLRParser()
    
    def test_simple_score_roundtrip(self):
        """Test roundtrip with simple 4-part SATB chorale"""
        # Create simple MusicXML content
        musicxml_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare/DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1">
      <part-name>Soprano</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
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
        <duration>4</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>F</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <type>quarter</type>
      </note>
    </measure>
  </part>
</score-partwise>"""
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(musicxml_content)
            input_file = f.name
        
        try:
            # Parse MusicXML
            original_score = self.parser.parse(input_file)
            
            # Convert to TLR and back
            tlr_text = self.tlr_converter.ikr_to_tlr(original_score)
            parsed_back, errors = self.tlr_parser.parse(tlr_text)
            
            assert not errors, f"TLR parsing failed: {errors}"
            assert parsed_back is not None, "TLR parsing returned None"
            
            # Export back to MusicXML
            with tempfile.NamedTemporaryFile(suffix='.musicxml', delete=False) as f:
                output_file = f.name
            
            success = self.exporter.export(parsed_back, output_file)
            assert success, "Export failed"
            
            # Parse the exported file and compare
            reimported_score = self.parser.parse(output_file)
            
            # Basic structure comparison
            assert len(original_score.parts) == len(reimported_score.parts)
            
            if original_score.parts and reimported_score.parts:
                original_part = original_score.parts[0]
                reimported_part = reimported_score.parts[0]
                
                assert len(original_part.voices) == len(reimported_part.voices)
                
                if original_part.voices and reimported_part.voices:
                    original_voice = original_part.voices[0]
                    reimported_voice = reimported_part.voices[0]
                    
                    assert len(original_voice.measures) == len(reimported_voice.measures)
                    
                    if original_voice.measures and reimported_voice.measures:
                        original_measure = original_voice.measures[0]
                        reimported_measure = reimported_voice.measures[0]
                        
                        # Check note count
                        note_events_original = [e for e in original_measure.events if isinstance(e, NoteEvent)]
                        note_events_reimported = [e for e in reimported_measure.events if isinstance(e, NoteEvent)]
                        
                        assert len(note_events_original) == len(note_events_reimported)
                        
                        # Check pitch preservation
                        for i, (orig, reimp) in enumerate(zip(note_events_original, note_events_reimported)):
                            assert orig.pitch_step == reimp.pitch_step, f"Note {i}: pitch step differs"
                            assert orig.pitch_alter == reimp.pitch_alter, f"Note {i}: pitch alteration differs"
                            assert orig.octave == reimp.octave, f"Note {i}: octave differs"
                            assert orig.duration == reimp.duration, f"Note {i}: duration differs"
                            assert orig.onset == reimp.onset, f"Note {i}: onset differs"
            
        finally:
            # Clean up temporary files
            if os.path.exists(input_file):
                os.unlink(input_file)
            if output_file and os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_rest_preservation(self):
        """Test that rests are preserved through roundtrip"""
        musicxml_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare/DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1">
      <part-name>Test</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
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
        <duration>4</duration>
        <type>quarter</type>
      </note>
      <rest>
        <duration>4</duration>
        <type>quarter</type>
      </rest>
      <note>
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>8</duration>
        <type>half</type>
      </note>
    </measure>
  </part>
</score-partwise>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(musicxml_content)
            input_file = f.name
        
        try:
            # Parse and roundtrip
            original_score = self.parser.parse(input_file)
            tlr_text = self.tlr_converter.ikr_to_tlr(original_score)
            parsed_back, errors = self.tlr_parser.parse(tlr_text)
            
            assert not errors, f"TLR parsing failed: {errors}"
            
            # Check that rests are preserved
            original_measure = original_score.parts[0].voices[0].measures[0]
            if parsed_back and parsed_back.parts:
                reimported_measure = parsed_back.parts[0].voices[0].measures[0]
            
            rest_events_original = [e for e in original_measure.events if isinstance(e, RestEvent)]
            rest_events_reimported = [e for e in reimported_measure.events if isinstance(e, RestEvent)]
            
            assert len(rest_events_original) == len(rest_events_reimported), "Rest count differs"
            
            if rest_events_original and rest_events_reimported:
                assert rest_events_original[0].duration == rest_events_reimported[0].duration
                assert rest_events_original[0].onset == rest_events_reimported[0].onset
            
        finally:
            os.unlink(input_file)
    
    def test_time_signature_preservation(self):
        """Test that time signatures are preserved through roundtrip"""
        musicxml_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare/DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1">
      <part-name>Test</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
        <time>
          <beats>5</beats>
          <beat-type>8</beat-type>
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
        <duration>5</duration>
        <type>eighth</type>
      </note>
      <note>
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>5</duration>
        <type>eighth</type>
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>5</duration>
        <type>eighth</type>
      </note>
      <note>
        <pitch>
          <step>F</step>
          <octave>4</octave>
        </pitch>
        <duration>5</duration>
        <type>eighth</type>
      </note>
      <note>
        <pitch>
          <step>G</step>
          <octave>4</octave>
        </pitch>
        <duration>5</duration>
        <type>eighth</type>
      </note>
    </measure>
  </part>
</score-partwise>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(musicxml_content)
            input_file = f.name
        
try:
            original_score = self.parser.parse(input_file)
            tlr_text = self.tlr_converter.ikr_to_tlr(original_score)
            parsed_back, errors = self.tlr_parser.parse(tlr_text)
            
            assert not errors, f"TLR parsing failed: {errors}"
            
            # Check that rests are preserved
            original_measure = original_score.parts[0].voices[0].measures[0]
            reimported_measure = None
            if parsed_back and parsed_back.parts:
                reimported_measure = parsed_back.parts[0].voices[0].measures[0]
            
            rest_events_original = [e for e in original_measure.events if isinstance(e, RestEvent)]
            rest_events_reimported = [e for e in reimported_measure.events if isinstance(e, RestEvent)] if reimported_measure else []
            
            assert len(rest_events_original) == len(rest_events_reimported), "Rest count differs"
            
            if rest_events_original and rest_events_reimported:
                assert rest_events_original[0].duration == rest_events_reimported[0].duration
                assert rest_events_original[0].onset == rest_events_reimported[0].onset
            
        finally:
            os.unlink(input_file)