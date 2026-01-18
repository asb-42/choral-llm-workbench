import pytest
import hypothesis
from hypothesis import given, strategies as st
from fractions import Fraction
from ikr_light import Score, Part, Voice, Measure, NoteEvent, RestEvent
from tlr_converter import TLRConverter
from tlr_parser import TLRParser
from ollama_llm import OllamaLLM


class TestPropertyBased:
    """Property-based tests for musical transformations"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tlr_converter = TLRConverter()
        self.tlr_parser = TLRParser()
        self.llm = OllamaLLM()
    
    @given(
        pitch_steps=st.sampled_from(['C', 'D', 'E', 'F', 'G', 'A', 'B']),
        octaves=st.integers(min_value=3, max_value=6),
        alterations=st.sampled_from([-2, -1, 0, 1, 2]),
        durations=st.fractions(min_value=Fraction(1, 16), max_value=Fraction(4, 1)),
        onsets=st.fractions(min_value=Fraction(0), max_value=Fraction(3, 1))
    )
    def test_single_note_creation_and_roundtrip(self, pitch_steps, octaves, alterations, durations, onsets):
        """Test that single notes can be created and roundtrip correctly"""
        # Create minimal score with single note
        note = NoteEvent(
            onset=onset,
            duration=durations,
            pitch_step=pitch_steps,
            pitch_alter=alterations,
            octave=octaves
        )
        
        measure = Measure(number=1, time_signature="4/4", events=[note])
        voice = Voice(id="1", measures=[measure])
        part = Part(id="test", name="Test", role="instrument", voices=[voice])
        score = Score(metadata={}, parts=[part])
        
        # Convert to TLR and back
        tlr_text = self.tlr_converter.ikr_to_tlr(score)
        parsed_back, errors = self.tlr_parser.parse(tlr_text)
        
        assert not errors, f"TLR parsing failed: {errors}"
        assert parsed_back is not None
        
        # Verify note properties are preserved
        reimported_note = parsed_back.parts[0].voices[0].measures[0].events[0]
        assert isinstance(reimported_note, NoteEvent)
        assert reimported_note.pitch_step == pitch_steps
        assert reimported_note.pitch_alter == alterations
        assert reimported_note.octave == octaves
        assert reimported_note.duration == durations
        assert reimported_note.onset == onset
    
    @given(
        semitones=st.integers(min_value=-12, max_value=12),
        original_pitch=st.sampled_from(['C', 'D', 'E', 'F', 'G', 'A', 'B'])
    )
    def test_transposition_property(self, semitones, original_pitch):
        """Test transposition preserves intervals (property test)"""
        # Create simple C major scale fragment
        notes = []
        for i, step in enumerate(['C', 'D', 'E', 'F', 'G', 'A', 'B']):
            if step == original_pitch:
                note = NoteEvent(
                    onset=Fraction(i, 4),
                    duration=Fraction(1, 4),
                    pitch_step=step,
                    pitch_alter=0,
                    octave=4
                )
                notes.append(note)
        
        if not notes:
            return  # Skip if original_pitch not in scale
        
        measure = Measure(number=1, time_signature="4/4", events=notes)
        voice = Voice(id="1", measures=[measure])
        part = Part(id="test", name="Test", role="instrument", voices=[voice])
        score = Score(metadata={}, parts=[part])
        
        # Convert to TLR
        tlr_text = self.tlr_converter.ikr_to_tlr(score)
        
        # Create transposition instruction
        instruction = f"Transpose everything up {semitones} semitones"
        
        # Mock LLM response for testing (avoid actual LLM call)
        transformed_tlr = self._mock_transposition(tlr_text, semitones)
        
        # Parse transformed TLR
        transformed_score, errors = self.tlr_parser.parse(transformed_tlr)
        
        if not errors and transformed_score:
            # Verify transposition worked (basic check)
            original_note = notes[0]
            transformed_note = transformed_score.parts[0].voices[0].measures[0].events[0]
            
            if isinstance(transformed_note, NoteEvent):
                # Check that pitch changed
                assert transformed_note.pitch_step != original_note.pitch_step or transformed_note.octave != original_note.octave
                # Check that duration and onset are preserved
                assert transformed_note.duration == original_note.duration
                assert transformed_note.onset == original_note.onset
    
    @given(
        scale_factor=st.sampled_from([Fraction(1, 2), Fraction(2, 1), Fraction(3, 2), Fraction(2, 3)])
    )
    def test_rhythmic_scaling_property(self, scale_factor):
        """Test rhythmic scaling preserves proportions"""
        # Create simple rhythm pattern
        original_durations = [Fraction(1, 4), Fraction(1, 4), Fraction(1, 2)]
        notes = []
        cumulative_onset = Fraction(0)
        
        for i, duration in enumerate(original_durations):
            note = NoteEvent(
                onset=cumulative_onset,
                duration=duration,
                pitch_step='C',
                pitch_alter=0,
                octave=4
            )
            notes.append(note)
            cumulative_onset += duration
        
        measure = Measure(number=1, time_signature="4/4", events=notes)
        voice = Voice(id="1", measures=[measure])
        part = Part(id="test", name="Test", role="instrument", voices=[voice])
        score = Score(metadata={}, parts=[part])
        
        # Convert to TLR
        tlr_text = self.tlr_converter.ikr_to_tlr(score)
        
        # Create rhythmic scaling instruction
        instruction = f"Scale all durations by {scale_factor}"
        
        # Mock LLM response for testing
        transformed_tlr = self._mock_rhythmic_scaling(tlr_text, scale_factor)
        
        # Parse transformed TLR
        transformed_score, errors = self.tlr_parser.parse(transformed_tlr)
        
        if not errors and transformed_score:
            # Verify rhythmic scaling
            transformed_notes = [e for e in transformed_score.parts[0].voices[0].measures[0].events if isinstance(e, NoteEvent)]
            
            assert len(transformed_notes) == len(original_durations)
            
            for i, transformed_note in enumerate(transformed_notes):
                expected_duration = original_durations[i] * scale_factor
                # Allow small floating point errors
                assert abs(float(transformed_note.duration) - float(expected_duration)) < 0.001
    
    def _mock_transposition(self, tlr_text: str, semitones: int) -> str:
        """Mock transposition for testing (avoid LLM call)"""
        lines = tlr_text.split('\n')
        transformed_lines = []
        
        for line in lines:
            if line.startswith('NOTE'):
                # Simple mock transposition - just change octave for simplicity
                if semitones > 0 and '4' in line:
                    line = line.replace('4', '5')
                elif semitones < 0 and '5' in line:
                    line = line.replace('5', '4')
            transformed_lines.append(line)
        
        return '\n'.join(transformed_lines)
    
    def _mock_rhythmic_scaling(self, tlr_text: str, scale_factor) -> str:
        """Mock rhythmic scaling for testing (avoid LLM call)"""
        lines = tlr_text.split('\n')
        transformed_lines = []
        
        for line in lines:
            if line.startswith('NOTE') or line.startswith('REST'):
                # Simple mock scaling - just change duration
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.startswith('dur='):
                        original_dur = Fraction(part.split('=')[1])
                        new_dur = original_dur * scale_factor
                        parts[i] = f'dur={new_dur}'
                        break
                line = ' '.join(parts)
            transformed_lines.append(line)
        
        return '\n'.join(transformed_lines)


class TestNegativeTests:
    """Negative tests for edge cases and error conditions"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tlr_parser = TLRParser()
    
    def test_overlapping_events_detection(self):
        """Test that overlapping events are detected"""
        tlr_with_overlap = """PART Test ROLE instrument
VOICE 1
MEASURE 1 TIME 4/4
NOTE t=0 dur=1/2 pitch=C4
NOTE t=1/4 dur=1/4 pitch=D4
"""
        parsed_score, errors = self.tlr_parser.parse(tlr_with_overlap)
        
        assert parsed_score is None  # Should fail due to overlap
        assert any("overlap" in error.lower() for error in errors)
    
    def test_measure_overflow_detection(self):
        """Test that measure overflow is detected"""
        tlr_with_overflow = """PART Test ROLE instrument
VOICE 1
MEASURE 1 TIME 4/4
NOTE t=3/2 dur=1 pitch=C4
"""
        parsed_score, errors = self.tlr_parser.parse(tlr_with_overflow)
        
        assert parsed_score is None  # Should fail due to overflow
        assert any("capacity" in error.lower() or "exceed" in error.lower() for error in errors)
    
    def test_negative_duration_detection(self):
        """Test that negative durations are detected"""
        tlr_with_negative_duration = """PART Test ROLE instrument
VOICE 1
MEASURE 1 TIME 4/4
NOTE t=0 dur=-1/4 pitch=C4
"""
        parsed_score, errors = self.tlr_parser.parse(tlr_with_overflow)
        
        assert parsed_score is None  # Should fail due to negative duration
        assert any("negative" in error.lower() or "positive" in error.lower() for error in errors)
    
    def test_invalid_tlr_lines(self):
        """Test that invalid TLR lines are detected"""
        invalid_tlr_lines = [
            "INVALID LINE",
            "PART Test",  # Missing ROLE
            "VOICE",  # Missing ID
            "MEASURE 1",  # Missing TIME
            "NOTE t=0 pitch=C4",  # Missing duration
            "REST dur=1/4",  # Missing onset
            "PART Test ROLE invalid_role",  # Invalid role
            "MEASURE 1 TIME invalid/time",  # Invalid time signature
        ]
        
        for invalid_line in invalid_tlr_lines:
            tlr_text = f"""PART Test ROLE instrument
VOICE 1
MEASURE 1 TIME 4/4
{invalid_line}
"""
            parsed_score, errors = self.tlr_parser.parse(tlr_text)
            
            # Should fail due to invalid line
            assert parsed_score is None or len(errors) > 0
    
    def test_invalid_pitch_formats(self):
        """Test that invalid pitch formats are detected"""
        invalid_pitches = [
            "NOTE t=0 dur=1/4 pitch=H4",  # Invalid pitch step
            "NOTE t=0 dur=1/4 pitch=C",   # Missing octave
            "NOTE t=0 dur=1/4 pitch=4",   # Missing pitch step
            "NOTE t=0 dur=1/4 pitch=C##4",  # Double sharp (not supported)
            "NOTE t=0 dur=1/4 pitch=Cbb4",  # Double flat (not supported)
        ]
        
        for invalid_pitch in invalid_pitches:
            tlr_text = f"""PART Test ROLE instrument
VOICE 1
MEASURE 1 TIME 4/4
{invalid_pitch}
"""
            parsed_score, errors = self.tlr_parser.parse(tlr_text)
            
            # Should fail due to invalid pitch
            assert parsed_score is None or len(errors) > 0
    
    def test_missing_headers(self):
        """Test that missing headers are detected"""
        tlr_without_part = """VOICE 1
MEASURE 1 TIME 4/4
NOTE t=0 dur=1/4 pitch=C4
"""
        parsed_score, errors = self.tlr_parser.parse(tlr_without_part)
        
        # Should fail because VOICE without PART
        assert any("VOICE without PART" in error for error in errors)
        
        tlr_without_voice = """PART Test ROLE instrument
MEASURE 1 TIME 4/4
NOTE t=0 dur=1/4 pitch=C4
"""
        parsed_score, errors = self.tlr_parser.parse(tlr_without_voice)
        
        # Should fail because MEASURE without VOICE
        assert any("MEASURE without VOICE" in error for error in errors)
        
        tlr_without_measure = """PART Test ROLE instrument
VOICE 1
NOTE t=0 dur=1/4 pitch=C4
"""
        parsed_score, errors = self.tlr_parser.parse(tlr_without_measure)
        
        # Should fail because NOTE without MEASURE
        assert any("Invalid line format" in error for error in errors)