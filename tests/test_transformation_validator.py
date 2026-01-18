import pytest
from transformation_validator import TransformationValidator
from ikr_light import Score, Part, Voice, Measure, NoteEvent, HarmonyEvent
from fractions import Fraction


class TestTransformationValidator:
    """Test transformation validation and hard barriers"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.validator = TransformationValidator()
    
    def test_allowed_transformations_structure(self):
        """Test that allowed transformations are properly defined"""
        expected_flags = ['transpose', 'rhythm_simplify', 'style_change', 'harmonic_reharm']
        
        assert set(self.validator.allowed_transformations.keys()) == set(expected_flags)
        
        for flag in expected_flags:
            config = self.validator.allowed_transformations[flag]
            assert 'description' in config
            assert 'allowed_changes' in config
            assert 'forbidden_changes' in config
            assert 'validation_rules' in config
    
    def test_transpose_validation_success(self):
        """Test successful transposition validation"""
        # Original score
        orig_notes = [
            NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='C', pitch_alter=0, octave=4),
            NoteEvent(onset=Fraction(1, 4), duration=Fraction(1, 4), pitch_step='D', pitch_alter=0, octave=4),
            NoteEvent(onset=Fraction(1, 2), duration=Fraction(1, 2), pitch_step='E', pitch_alter=0, octave=4)
        ]
        
        # Transposed score (up by major third)
        trans_notes = [
            NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='E', pitch_alter=0, octave=4),
            NoteEvent(onset=Fraction(1, 4), duration=Fraction(1, 4), pitch_step='F', pitch_alter=1, octave=4),
            NoteEvent(onset=Fraction(1, 2), duration=Fraction(1, 2), pitch_step='G', pitch_alter=1, octave=4)
        ]
        
        orig_measure = Measure(number=1, time_signature="4/4", events=orig_notes)
        trans_measure = Measure(number=1, time_signature="4/4", events=trans_notes)
        
        orig_voice = Voice(id="1", measures=[orig_measure])
        trans_voice = Voice(id="1", measures=[trans_measure])
        
        orig_part = Part(id="test", name="Test", role="instrument", voices=[orig_voice])
        trans_part = Part(id="test", name="Test", role="instrument", voices=[trans_voice])
        
        orig_score = Score(metadata={}, parts=[orig_part])
        trans_score = Score(metadata={}, parts=[trans_part])
        
        # Validate
        is_valid, errors = self.validator.validate_transformation(
            orig_score, trans_score, {'transpose'}
        )
        
        assert is_valid, f"Transposition should be valid: {errors}"
    
    def test_transpose_validation_failure_inconsistent(self):
        """Test transposition validation failure due to inconsistency"""
        # Original score
        orig_notes = [
            NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='C', pitch_alter=0, octave=4),
            NoteEvent(onset=Fraction(1, 4), duration=Fraction(1, 4), pitch_step='D', pitch_alter=0, octave=4)
        ]
        
        # Badly transposed score (inconsistent intervals)
        trans_notes = [
            NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='E', pitch_alter=0, octave=4),  # +3 semitones
            NoteEvent(onset=Fraction(1, 4), duration=Fraction(1, 4), pitch_step='F', pitch_alter=0, octave=4)   # +2 semitones
        ]
        
        orig_measure = Measure(number=1, time_signature="4/4", events=orig_notes)
        trans_measure = Measure(number=1, time_signature="4/4", events=trans_notes)
        
        orig_voice = Voice(id="1", measures=[orig_measure])
        trans_voice = Voice(id="1", measures=[trans_measure])
        
        orig_part = Part(id="test", name="Test", role="instrument", voices=[orig_voice])
        trans_part = Part(id="test", name="Test", role="instrument", voices=[trans_voice])
        
        orig_score = Score(metadata={}, parts=[orig_part])
        trans_score = Score(metadata={}, parts=[trans_part])
        
        # Validate
        is_valid, errors = self.validator.validate_transformation(
            orig_score, trans_score, {'transpose'}
        )
        
        assert not is_valid, "Inconsistent transposition should be invalid"
        assert any("consistent" in error.lower() for error in errors)
    
    def test_rhythm_simplification_validation_success(self):
        """Test successful rhythm simplification"""
        # Original complex rhythm
        orig_notes = [
            NoteEvent(onset=Fraction(0), duration=Fraction(3, 8), pitch_step='C', pitch_alter=0, octave=4),
            NoteEvent(onset=Fraction(3, 8), duration=Fraction(1, 8), pitch_step='D', pitch_alter=0, octave=4)
        ]
        
        # Simplified rhythm
        trans_notes = [
            NoteEvent(onset=Fraction(0), duration=Fraction(1, 2), pitch_step='C', pitch_alter=0, octave=4),
            NoteEvent(onset=Fraction(1, 2), duration=Fraction(1, 2), pitch_step='D', pitch_alter=0, octave=4)
        ]
        
        orig_measure = Measure(number=1, time_signature="4/4", events=orig_notes)
        trans_measure = Measure(number=1, time_signature="4/4", events=trans_notes)
        
        orig_voice = Voice(id="1", measures=[orig_measure])
        trans_voice = Voice(id="1", measures=[trans_measure])
        
        orig_part = Part(id="test", name="Test", role="instrument", voices=[orig_voice])
        trans_part = Part(id="test", name="Test", role="instrument", voices=[trans_voice])
        
        orig_score = Score(metadata={}, parts=[orig_part])
        trans_score = Score(metadata={}, parts=[trans_part])
        
        # Validate
        is_valid, errors = self.validator.validate_transformation(
            orig_score, trans_score, {'rhythm_simplify'}
        )
        
        assert is_valid, f"Rhythm simplification should be valid: {errors}"
    
    def test_style_change_validation_failure_structure_change(self):
        """Test style change validation failure due to structure change"""
        # Original score
        orig_measure = Measure(number=1, time_signature="4/4", events=[
            NoteEvent(onset=Fraction(0), duration=Fraction(1), pitch_step='C', pitch_alter=0, octave=4)
        ])
        orig_voice = Voice(id="1", measures=[orig_measure])
        orig_part = Part(id="test", name="Test", role="instrument", voices=[orig_voice])
        orig_score = Score(metadata={}, parts=[orig_part])
        
        # Changed structure (removed measure)
        trans_voice = Voice(id="1", measures=[])  # Empty!
        trans_part = Part(id="test", name="Test", role="instrument", voices=[trans_voice])
        trans_score = Score(metadata={}, parts=[trans_part])
        
        # Validate
        is_valid, errors = self.validator.validate_transformation(
            orig_score, trans_score, {'style_change'}
        )
        
        assert not is_valid, "Structure change should be invalid"
        assert any("measure structure" in error.lower() for error in errors)
    
    def test_harmonic_reharm_validation_success(self):
        """Test successful harmonic reharmonization"""
        # Original harmony
        orig_harmony = HarmonyEvent(onset=Fraction(0), harmony="I")
        
        # Reharmonized harmony
        trans_harmony = HarmonyEvent(onset=Fraction(0), harmony="IV")
        
        # Same melody notes
        melody_notes = [
            NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='C', pitch_alter=0, octave=4),
            NoteEvent(onset=Fraction(1, 4), duration=Fraction(1, 4), pitch_step='E', pitch_alter=0, octave=4),
            NoteEvent(onset=Fraction(1, 2), duration=Fraction(1, 2), pitch_step='G', pitch_alter=0, octave=4)
        ]
        
        orig_measure = Measure(number=1, time_signature="4/4", events=melody_notes + [orig_harmony])
        trans_measure = Measure(number=1, time_signature="4/4", events=melody_notes + [trans_harmony])
        
        orig_voice = Voice(id="1", measures=[orig_measure])
        trans_voice = Voice(id="1", measures=[trans_measure])
        
        orig_part = Part(id="test", name="Test", role="instrument", voices=[orig_voice])
        trans_part = Part(id="test", name="Test", role="instrument", voices=[trans_voice])
        
        orig_score = Score(metadata={}, parts=[orig_part])
        trans_score = Score(metadata={}, parts=[trans_part])
        
        # Validate
        is_valid, errors = self.validator.validate_transformation(
            orig_score, trans_score, {'harmonic_reharm'}
        )
        
        assert is_valid, f"Harmonic reharm should be valid: {errors}"
    
    def test_harmonic_reharm_validation_failure_melody_change(self):
        """Test harmonic reharmonization validation failure due to melody change"""
        # Original melody
        orig_notes = [
            NoteEvent(onset=Fraction(0), duration=Fraction(1), pitch_step='C', pitch_alter=0, octave=4),
            NoteEvent(onset=Fraction(1, 4), duration=Fraction(3, 4), pitch_step='G', pitch_alter=0, octave=4)
        ]
        
        # Changed melody (should be invalid for harmonic_reharm)
        trans_notes = [
            NoteEvent(onset=Fraction(0), duration=Fraction(1), pitch_step='C', pitch_alter=0, octave=4),
            NoteEvent(onset=Fraction(1, 4), duration=Fraction(3, 4), pitch_step='A', pitch_alter=0, octave=4)  # Changed pitch
        ]
        
        orig_measure = Measure(number=1, time_signature="4/4", events=orig_notes)
        trans_measure = Measure(number=1, time_signature="4/4", events=trans_notes)
        
        orig_voice = Voice(id="1", measures=[orig_measure])
        trans_voice = Voice(id="1", measures=[trans_measure])
        
        orig_part = Part(id="test", name="Test", role="instrument", voices=[orig_voice])
        trans_part = Part(id="test", name="Test", role="instrument", voices=[trans_voice])
        
        orig_score = Score(metadata={}, parts=[orig_part])
        trans_score = Score(metadata={}, parts=[trans_part])
        
        # Validate
        is_valid, errors = self.validator.validate_transformation(
            orig_score, trans_score, {'harmonic_reharm'}
        )
        
        assert not is_valid, "Melody change should be invalid for harmonic_reharm"
        assert any("melody" in error.lower() for error in errors)
    
    def test_no_flags_rejection(self):
        """Test rejection when no transformation flags are set"""
        orig_measure = Measure(number=1, time_signature="4/4", events=[
            NoteEvent(onset=Fraction(0), duration=Fraction(1), pitch_step='C', pitch_alter=0, octave=4)
        ])
        orig_voice = Voice(id="1", measures=[orig_measure])
        orig_part = Part(id="test", name="Test", role="instrument", voices=[orig_voice])
        orig_score = Score(metadata={}, parts=[orig_part])
        
        trans_measure = Measure(number=1, time_signature="4/4", events=[
            NoteEvent(onset=Fraction(0), duration=Fraction(1), pitch_step='D', pitch_alter=0, octave=4)
        ])
        trans_voice = Voice(id="1", measures=[trans_measure])
        trans_part = Part(id="test", name="Test", role="instrument", voices=[trans_voice])
        trans_score = Score(metadata={}, parts=[trans_part])
        
        # Validate with no flags
        is_valid, errors = self.validator.validate_transformation(
            orig_score, trans_score, set()
        )
        
        assert not is_valid, "No flags should be rejected"
        assert any("No transformation flags" in error for error in errors)
    
    def test_unknown_flag_rejection(self):
        """Test rejection of unknown transformation flags"""
        orig_measure = Measure(number=1, time_signature="4/4", events=[
            NoteEvent(onset=Fraction(0), duration=Fraction(1), pitch_step='C', pitch_alter=0, octave=4)
        ])
        orig_voice = Voice(id="1", measures=[orig_measure])
        orig_part = Part(id="test", name="Test", role="instrument", voices=[orig_voice])
        orig_score = Score(metadata={}, parts=[orig_part])
        
        trans_measure = Measure(number=1, time_signature="4/4", events=[
            NoteEvent(onset=Fraction(0), duration=Fraction(1), pitch_step='D', pitch_alter=0, octave=4)
        ])
        trans_voice = Voice(id="1", measures=[trans_measure])
        trans_part = Part(id="test", name="Test", role="instrument", voices=[trans_voice])
        trans_score = Score(metadata={}, parts=[trans_part])
        
        # Validate with unknown flag
        is_valid, errors = self.validator.validate_transformation(
            orig_score, trans_score, {'unknown_transformation'}
        )
        
        assert not is_valid, "Unknown flag should be rejected"
        assert any("Unknown transformation flag" in error for error in errors)
    
    def test_prompt_additions_generation(self):
        """Test prompt additions generation for transformation flags"""
        # Single flag
        prompt = self.validator.get_transformation_prompt_additions({'transpose'})
        assert "ALLOWED TRANSFORMATIONS:" in prompt
        assert "TRANSPOSE: Change pitch by semitones" in prompt
        assert "Only perform explicitly allowed transformations" in prompt
        
        # Multiple flags
        prompt = self.validator.get_transformation_prompt_additions({'transpose', 'rhythm_simplify'})
        assert "TRANSPOSE: Change pitch by semitones" in prompt
        assert "RHYTHM_SIMPLIFY: Simplify rhythmic patterns" in prompt
        
        # No flags
        prompt = self.validator.get_transformation_prompt_additions(set())
        assert prompt == ""
    
    def test_note_to_midi_conversion(self):
        """Test MIDI note conversion"""
        # C4 = MIDI 60
        midi = self.validator._note_to_midi(
            NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='C', pitch_alter=0, octave=4)
        )
        assert midi == 60
        
        # C#4 = MIDI 61
        midi = self.validator._note_to_midi(
            NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='C', pitch_alter=1, octave=4)
        )
        assert midi == 61
        
        # Cb4 = MIDI 59
        midi = self.validator._note_to_midi(
            NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='C', pitch_alter=-1, octave=4)
        )
        assert midi == 59
        
        # Invalid note
        midi = self.validator._note_to_midi(None)
        assert midi is None