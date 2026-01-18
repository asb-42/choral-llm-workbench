import pytest
from helmholtz_converter import HelmholtzConverter
from ikr_light import Score, Part, Voice, Measure, NoteEvent
from fractions import Fraction


class TestHelmholtzConverter:
    """Test Helmholtz notation conversion"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.converter = HelmholtzConverter()
    
    def test_c4_to_helmholtz(self):
        """Test C4 conversion (middle C)"""
        note = NoteEvent(
            onset=Fraction(0),
            duration=Fraction(1, 4),
            pitch_step='C',
            pitch_alter=0,
            octave=4
        )
        
        result = self.converter.note_to_helmholtz(note)
        assert result == 'c'
    
    def test_a4_to_helmholtz(self):
        """Test A4 conversion (concert A)"""
        note = NoteEvent(
            onset=Fraction(0),
            duration=Fraction(1, 4),
            pitch_step='A',
            pitch_alter=0,
            octave=4
        )
        
        result = self.converter.note_to_helmholtz(note)
        assert result == 'a'
    
    def test_c5_to_helmholtz(self):
        """Test C5 conversion (high C)"""
        note = NoteEvent(
            onset=Fraction(0),
            duration=Fraction(1, 4),
            pitch_step='C',
            pitch_alter=0,
            octave=5
        )
        
        result = self.converter.note_to_helmholtz(note)
        assert result == "c'"
    
    def test_c3_to_helmholtz(self):
        """Test C3 conversion (low C)"""
        note = NoteEvent(
            onset=Fraction(0),
            duration=Fraction(1, 4),
            pitch_step='C',
            pitch_alter=0,
            octave=3
        )
        
        result = self.converter.note_to_helmholtz(note)
        assert result == 'C,'
    
    def test_sharp_notes(self):
        """Test sharp accidentals"""
        note = NoteEvent(
            onset=Fraction(0),
            duration=Fraction(1, 4),
            pitch_step='F',
            pitch_alter=1,
            octave=4
        )
        
        result = self.converter.note_to_helmholtz(note)
        assert result == 'f♯'
    
    def test_flat_notes(self):
        """Test flat accidentals (non-B)"""
        note = NoteEvent(
            onset=Fraction(0),
            duration=Fraction(1, 4),
            pitch_step='E',
            pitch_alter=-1,
            octave=4
        )
        
        result = self.converter.note_to_helmholtz(note)
        assert result == 'e♭'
    
    def test_b_flat_special_case(self):
        """Test B-flat special case"""
        note = NoteEvent(
            onset=Fraction(0),
            duration=Fraction(1, 4),
            pitch_step='B',
            pitch_alter=-1,
            octave=4
        )
        
        result = self.converter.note_to_helmholtz(note)
        assert result == 'b'
    
    def test_b_natural_special_case(self):
        """Test B natural special case"""
        note = NoteEvent(
            onset=Fraction(0),
            duration=Fraction(1, 4),
            pitch_step='B',
            pitch_alter=0,
            octave=4
        )
        
        result = self.converter.note_to_helmholtz(note)
        assert result == 'b♮'
    
    def test_tied_notes(self):
        """Test tie notation"""
        note_start = NoteEvent(
            onset=Fraction(0),
            duration=Fraction(1, 4),
            pitch_step='C',
            pitch_alter=0,
            octave=4,
            tie="start"
        )
        
        note_stop = NoteEvent(
            onset=Fraction(1, 4),
            duration=Fraction(1, 4),
            pitch_step='C',
            pitch_alter=0,
            octave=4,
            tie="stop"
        )
        
        result_start = self.converter.note_to_helmholtz(note_start)
        result_stop = self.converter.note_to_helmholtz(note_stop)
        
        assert result_start == 'c～'
        assert result_stop == 'c～'
    
    def test_duration_to_text(self):
        """Test duration conversion to readable text"""
        assert self.converter.duration_to_helmholtz_text(Fraction(1, 4)) == "quarter"
        assert self.converter.duration_to_helmholtz_text(Fraction(1, 2)) == "half"
        assert self.converter.duration_to_helmholtz_text(Fraction(1, 1)) == "whole"
        assert self.converter.duration_to_helmholtz_text(Fraction(1, 8)) == "eighth"
        assert self.converter.duration_to_helmholtz_text(Fraction(3, 4)) == "dotted half"
    
    def test_simple_score_to_helmholtz(self):
        """Convert simple score to Helmholtz TLR"""
        # Create simple score
        note1 = NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='C', pitch_alter=0, octave=4)
        note2 = NoteEvent(onset=Fraction(1, 4), duration=Fraction(1, 4), pitch_step='D', pitch_alter=0, octave=4)
        
        measure = Measure(number=1, time_signature="4/4", events=[note1, note2])
        voice = Voice(id="1", measures=[measure])
        part = Part(id="test", name="Test", role="instrument", voices=[voice])
        score = Score(metadata={}, parts=[part])
        
        result = self.converter.score_to_helmholtz_tlr(score)
        
        # Check that it contains Helmholtz notation
        assert "PART Test ROLE instrument" in result
        assert "VOICE 1" in result
        assert "MEASURE 1 TIME 4/4" in result
        assert "NOTE t=0 dur=1/4 pitch=c (quarter)" in result
        assert "NOTE t=1/4 dur=1/4 pitch=d (quarter)" in result
    
    def test_dual_notation_display(self):
        """Test dual notation display function"""
        # Create simple score
        note = NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='C', pitch_alter=0, octave=4)
        measure = Measure(number=1, time_signature="4/4", events=[note])
        voice = Voice(id="1", measures=[measure])
        part = Part(id="test", name="Test", role="instrument", voices=[voice])
        score = Score(metadata={}, parts=[part])
        
        dual = self.converter.get_dual_notation_display(score)
        
        assert "spn" in dual
        assert "helmholtz" in dual
        assert "NOTE t=0 dur=1/4 pitch=C4" in dual["spn"]
        assert "NOTE t=0 dur=1/4 pitch=c (quarter)" in dual["helmholtz"]
    
    def test_side_by_side_comparison(self):
        """Test side-by-side comparison"""
        # Create simple score
        note = NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='C', pitch_alter=0, octave=4)
        measure = Measure(number=1, time_signature="4/4", events=[note])
        voice = Voice(id="1", measures=[measure])
        part = Part(id="test", name="Test", role="instrument", voices=[voice])
        score = Score(metadata={}, parts=[part])
        
        comparison = self.converter.create_side_by_side_comparison(score)
        
        assert "DUAL NOTATION DISPLAY" in comparison
        assert "SPN (left) | HELMHOLTZ (right)" in comparison
        assert "NOTE t=0 dur=1/4 pitch=C4" in comparison
        assert "NOTE t=0 dur=1/4 pitch=c (quarter)" in comparison
        assert "|" in comparison  # Separator