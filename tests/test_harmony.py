import pytest
from tlr_converter import TLRConverter
from tlr_parser import TLRParser
from helmholtz_converter import HelmholtzConverter
from ikr_light import Score, Part, Voice, Measure, NoteEvent, HarmonyEvent
from fractions import Fraction


class TestHarmonyEvents:
    """Test explicit Harmony events in TLR"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tlr_converter = TLRConverter()
        self.tlr_parser = TLRParser()
        self.helmholtz_converter = HelmholtzConverter()
    
    def test_simple_harmony_to_tlr(self):
        """Convert simple harmony event to TLR"""
        harmony = HarmonyEvent(onset=Fraction(0), harmony="IV")
        
        measure = Measure(number=1, time_signature="4/4", events=[harmony])
        voice = Voice(id="1", measures=[measure])
        part = Part(id="test", name="Test", role="instrument", voices=[voice])
        score = Score(metadata={}, parts=[part])
        
        tlr_text = self.tlr_converter.ikr_to_tlr(score)
        
        assert "HARMONY t=0 symbol=IV" in tlr_text
    
    def test_harmony_with_key_to_tlr(self):
        """Convert harmony event with key context to TLR"""
        harmony = HarmonyEvent(onset=Fraction(0), harmony="iv", key="E minor")
        
        measure = Measure(number=1, time_signature="4/4", events=[harmony])
        voice = Voice(id="1", measures=[measure])
        part = Part(id="test", name="Test", role="instrument", voices=[voice])
        score = Score(metadata={}, parts=[part])
        
        tlr_text = self.tlr_converter.ikr_to_tlr(score)
        
        assert "HARMONY t=0 symbol=iv key=E minor" in tlr_text
    
    def test_harmony_from_tlr(self):
        """Parse harmony event from TLR"""
        tlr_text = """PART Test ROLE instrument
VOICE 1
MEASURE 1 TIME 4/4
HARMONY t=0 symbol=IV
NOTE t=0 dur=1/4 pitch=C4
"""
        
        score, errors = self.tlr_parser.parse(tlr_text)
        
        assert not errors, f"Parse errors: {errors}"
        assert score is not None
        
        harmony_events = [e for e in score.parts[0].voices[0].measures[0].events 
                        if isinstance(e, HarmonyEvent)]
        assert len(harmony_events) == 1
        
        harmony = harmony_events[0]
        assert harmony.harmony == "IV"
        assert harmony.onset == Fraction(0)
        assert harmony.key is None
    
    def test_harmony_with_key_from_tlr(self):
        """Parse harmony event with key from TLR"""
        tlr_text = """PART Test ROLE instrument
VOICE 1
MEASURE 1 TIME 4/4
HARMONY t=0 symbol=iv key=E minor
NOTE t=0 dur=1/4 pitch=E4
"""
        
        score, errors = self.tlr_parser.parse(tlr_text)
        
        assert not errors, f"Parse errors: {errors}"
        assert score is not None
        
        harmony_events = [e for e in score.parts[0].voices[0].measures[0].events 
                        if isinstance(e, HarmonyEvent)]
        assert len(harmony_events) == 1
        
        harmony = harmony_events[0]
        assert harmony.harmony == "iv"
        assert harmony.key == "E minor"
        assert harmony.onset == Fraction(0)
    
    def test_harmony_roundtrip(self):
        """Test harmony event roundtrip through TLR"""
        original_harmony = HarmonyEvent(onset=Fraction(1, 2), harmony="V7", key="G major")
        
        note = NoteEvent(onset=Fraction(1, 2), duration=Fraction(1, 2), pitch_step='G', pitch_alter=0, octave=4)
        
        measure = Measure(number=1, time_signature="4/4", events=[note, original_harmony])
        voice = Voice(id="1", measures=[measure])
        part = Part(id="test", name="Test", role="instrument", voices=[voice])
        original_score = Score(metadata={}, parts=[part])
        
        # Convert to TLR and back
        tlr_text = self.tlr_converter.ikr_to_tlr(original_score)
        parsed_score, errors = self.tlr_parser.parse(tlr_text)
        
        assert not errors, f"Parse errors: {errors}"
        assert parsed_score is not None
        
        # Check harmony preservation
        harmony_events = [e for e in parsed_score.parts[0].voices[0].measures[0].events 
                        if isinstance(e, HarmonyEvent)]
        assert len(harmony_events) == 1
        
        parsed_harmony = harmony_events[0]
        assert parsed_harmony.harmony == original_harmony.harmony
        assert parsed_harmony.key == original_harmony.key
        assert parsed_harmony.onset == original_harmony.onset
    
    def test_harmony_with_notes(self):
        """Test harmony events combined with notes"""
        harmony = HarmonyEvent(onset=Fraction(0), harmony="I")
        note1 = NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='C', pitch_alter=0, octave=4)
        note2 = NoteEvent(onset=Fraction(1, 4), duration=Fraction(1, 4), pitch_step='E', pitch_alter=0, octave=4)
        note3 = NoteEvent(onset=Fraction(1, 2), duration=Fraction(1, 2), pitch_step='G', pitch_alter=0, octave=4)
        
        measure = Measure(number=1, time_signature="4/4", events=[note1, note2, note3, harmony])
        voice = Voice(id="1", measures=[measure])
        part = Part(id="test", name="Test", role="instrument", voices=[voice])
        score = Score(metadata={}, parts=[part])
        
        tlr_text = self.tlr_converter.ikr_to_tlr(score)
        
        # Check that both notes and harmony are present
        assert "NOTE t=0 dur=1/4 pitch=C4" in tlr_text
        assert "NOTE t=1/4 dur=1/4 pitch=E4" in tlr_text
        assert "NOTE t=1/2 dur=1/2 pitch=G4" in tlr_text
        assert "HARMONY t=0 symbol=I" in tlr_text
    
    def test_harmony_in_helmholtz_display(self):
        """Test that harmony events work with Helmholtz display"""
        harmony = HarmonyEvent(onset=Fraction(0), harmony="iv", key="E minor")
        note = NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='E', pitch_alter=0, octave=4)
        
        measure = Measure(number=1, time_signature="4/4", events=[note, harmony])
        voice = Voice(id="1", measures=[measure])
        part = Part(id="test", name="Test", role="instrument", voices=[voice])
        score = Score(metadata={}, parts=[part])
        
        helmholtz_text = self.helmholtz_converter.score_to_helmholtz_tlr(score)
        
        # Harmony events should remain unchanged in Helmholtz display
        assert "HARMONY t=0 symbol=iv key=E minor" in helmholtz_text
        assert "NOTE t=0 dur=1/4 pitch=e (quarter)" in helmholtz_text
    
    def test_multiple_harmony_events(self):
        """Test multiple harmony events in same measure"""
        harmony1 = HarmonyEvent(onset=Fraction(0), harmony="I")
        harmony2 = HarmonyEvent(onset=Fraction(1), harmony="IV")
        harmony3 = HarmonyEvent(onset=Fraction(2), harmony="V")
        
        measure = Measure(number=1, time_signature="4/4", events=[harmony1, harmony2, harmony3])
        voice = Voice(id="1", measures=[measure])
        part = Part(id="test", name="Test", role="instrument", voices=[voice])
        score = Score(metadata={}, parts=[part])
        
        tlr_text = self.tlr_converter.ikr_to_tlr(score)
        
        # Check all harmony events are present
        assert "HARMONY t=0 symbol=I" in tlr_text
        assert "HARMONY t=1 symbol=IV" in tlr_text
        assert "HARMONY t=2 symbol=V" in tlr_text
    
    def test_harmony_validation(self):
        """Test validation of harmony events"""
        # Test invalid harmony (missing symbol)
        invalid_tlr = """PART Test ROLE instrument
VOICE 1
MEASURE 1 TIME 4/4
HARMONY t=0 symbol=
"""
        score, errors = self.tlr_parser.parse(invalid_tlr)
        
        assert score is None or len(errors) > 0
        assert any("symbol cannot be empty" in error for error in errors)
    
    def test_harmony_with_various_chord_symbols(self):
        """Test various chord symbol formats"""
        chord_symbols = ["I", "IV", "V7", "ii°", "V/V", "Ger6", "N6", "Fr+6"]
        
        for symbol in chord_symbols:
            harmony = HarmonyEvent(onset=Fraction(0), harmony=symbol)
            
            measure = Measure(number=1, time_signature="4/4", events=[harmony])
            voice = Voice(id="1", measures=[measure])
            part = Part(id="test", name="Test", role="instrument", voices=[voice])
            score = Score(metadata={}, parts=[part])
            
            tlr_text = self.tlr_converter.ikr_to_tlr(score)
            parsed_score, errors = self.tlr_parser.parse(tlr_text)
            
            assert not errors, f"Failed for symbol {symbol}: {errors}"
            
            # Check symbol preservation
            harmony_events = [e for e in parsed_score.parts[0].voices[0].measures[0].events 
                            if isinstance(e, HarmonyEvent)]
            assert len(harmony_events) == 1
            assert harmony_events[0].harmony == symbol
    
    def test_harmony_system_prompt_example(self):
        """Test the exact example from system prompt"""
        tlr_text = """PART Test ROLE instrument
VOICE 1
MEASURE 1 TIME 4/4
HARMONY t=0 symbol=iv key=E minor
NOTE t=0 dur=1/4 pitch=E4
NOTE t=1/4 dur=1/4 pitch=G4
NOTE t=1/2 dur=1/2 pitch=B4
"""
        
        score, errors = self.tlr_parser.parse(tlr_text)
        
        assert not errors, f"Parse errors: {errors}"
        assert score is not None
        
        harmony_events = [e for e in score.parts[0].voices[0].measures[0].events 
                        if isinstance(e, HarmonyEvent)]
        assert len(harmony_events) == 1
        
        harmony = harmony_events[0]
        assert harmony.harmony == "iv"
        assert harmony.key == "E minor"
        assert harmony.onset == Fraction(0)