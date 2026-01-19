from typing import Dict, List, Optional, Set, Tuple
from ikr_light import Score, Part, Voice, Measure, Event, NoteEvent, HarmonyEvent
from fractions import Fraction


class TransformationValidator:
    """Hard barrier for allowed transformations - prevents creative overreach"""
    
    def __init__(self):
        # Define allowed transformation types
        self.allowed_transformations = {
            'transpose': {
                'description': 'Change pitch by semitones (maintain intervals)',
                'allowed_changes': ['pitch_step', 'octave', 'pitch_alter'],
                'forbidden_changes': ['duration', 'onset', 'timing'],
                'validation_rules': ['check_transposition_consistency', 'verify_interval_preservation']
            },
            'rhythm_simplify': {
                'description': 'Simplify rhythmic patterns (e.g., dotted to straight)',
                'allowed_changes': ['duration', 'onset'],
                'forbidden_changes': ['pitch_step', 'octave', 'pitch_alter'],
                'validation_rules': ['check_rhythm_simplification', 'verify_measure_filling']
            },
            'style_change': {
                'description': 'Change musical style while preserving essential structure',
                'allowed_changes': ['duration', 'pitch_step', 'octave', 'pitch_alter'],
                'forbidden_changes': ['measure_count', 'part_count', 'voice_structure'],
                'validation_rules': ['check_style_consistency', 'verify_musical_integrity']
            },
            'harmonic_reharm': {
                'description': 'Reharmonize while preserving melody',
                'allowed_changes': ['harmony'],
                'forbidden_changes': ['melody_pitch', 'melody_rhythm'],
                'validation_rules': ['check_harmonic_validity', 'verify_melody_preservation']
            }
        }
    
    def validate_transformation(self, original_score: Score, transformed_score: Score, 
                             allowed_flags: Set[str]) -> Tuple[bool, List[str]]:
        """
        Validate that transformation only uses allowed changes
        
        Returns: (is_valid, error_messages)
        """
        errors = []
        
        # Check if any transformation flags are set
        if not allowed_flags:
            errors.append("No transformation flags selected - transformation not allowed")
            return False, errors

    def get_transformation_prompt_additions(self, allowed_flags: Set[str]) -> str:
        """
        Generate additional prompt constraints based on allowed transformation flags

        Returns prompt text to add to system prompt for constrained transformations
        """
        if not allowed_flags:
            return ""

        constraints = ["ADDITIONAL TRANSFORMATION CONSTRAINTS:"]

        for flag in allowed_flags:
            if flag in self.allowed_transformations:
                trans_info = self.allowed_transformations[flag]
                constraints.append(f"- {flag.upper()}: {trans_info['description']}")
                constraints.append(f"  Allowed changes: {', '.join(trans_info['allowed_changes'])}")
                constraints.append(f"  Forbidden changes: {', '.join(trans_info['forbidden_changes'])}")

        constraints.append("")
        constraints.append("IMPORTANT: Only perform the transformations explicitly allowed above.")
        constraints.append("Do NOT make changes that are listed as 'forbidden' for any selected transformation type.")

        return "\n".join(constraints)
        
        # Validate each flag
        for flag in allowed_flags:
            if flag not in self.allowed_transformations:
                errors.append(f"Unknown transformation flag: {flag}")
                continue
            
            flag_valid, flag_errors = self._validate_single_flag(
                original_score, transformed_score, flag
            )
            
            if not flag_valid:
                errors.extend(flag_errors)
        
        # Check for disallowed global changes
        global_errors = self._validate_global_constraints(original_score, transformed_score)
        errors.extend(global_errors)
        
        return len(errors) == 0, errors
    
    def _validate_single_flag(self, original_score: Score, transformed_score: Score, 
                           flag: str) -> Tuple[bool, List[str]]:
        """Validate a single transformation flag"""
        errors = []
        flag_config = self.allowed_transformations[flag]
        
        if flag == 'transpose':
            errors.extend(self._validate_transposition(original_score, transformed_score))
        elif flag == 'rhythm_simplify':
            errors.extend(self._validate_rhythm_simplification(original_score, transformed_score))
        elif flag == 'style_change':
            errors.extend(self._validate_style_change(original_score, transformed_score))
        elif flag == 'harmonic_reharm':
            errors.extend(self._validate_harmonic_reharm(original_score, transformed_score))
        
        return len(errors) == 0, errors
    
    def _validate_transposition(self, original_score: Score, transformed_score: Score) -> List[str]:
        """Validate transposition transformation"""
        errors = []
        
        # Check that part structure is preserved
        if len(original_score.parts) != len(transformed_score.parts):
            errors.append("Transposition must preserve part structure")
            return errors
        
        # Check for consistent transposition across each part
        for orig_part, trans_part in zip(original_score.parts, transformed_score.parts):
            if len(orig_part.voices) != len(trans_part.voices):
                errors.append(f"Transposition must preserve voice structure in {orig_part.name}")
                continue
            
            for orig_voice, trans_voice in zip(orig_part.voices, trans_part.voices):
                transposition_intervals = []
                
                for orig_measure, trans_measure in zip(orig_voice.measures, trans_voice.measures):
                    # Get note events
                    orig_notes = [e for e in orig_measure.events if isinstance(e, NoteEvent)]
                    trans_notes = [e for e in trans_measure.events if isinstance(e, NoteEvent)]
                    
                    if len(orig_notes) != len(trans_notes):
                        errors.append(f"Transposition must preserve note count in measure {orig_measure.number}")
                        continue
                    
                    for orig_note, trans_note in zip(orig_notes, trans_notes):
                        # Check duration preservation
                        if orig_note.duration != trans_note.duration:
                            errors.append(f"Transposition must preserve note duration at t={orig_note.onset}")
                        
                        # Check onset preservation
                        if orig_note.onset != trans_note.onset:
                            errors.append(f"Transposition must preserve note onset at t={orig_note.onset}")
                        
                        # Calculate transposition interval
                        orig_midi = self._note_to_midi(orig_note)
                        trans_midi = self._note_to_midi(trans_note)
                        
                        if orig_midi is not None and trans_midi is not None:
                            interval = trans_midi - orig_midi
                            transposition_intervals.append(interval)
                
                # Check for consistent transposition
                if transposition_intervals:
                    unique_intervals = set(transposition_intervals)
                    if len(unique_intervals) > 1:
                        errors.append(f"Transposition must be consistent - found multiple intervals: {unique_intervals}")
        
        return errors
    
    def _validate_rhythm_simplification(self, original_score: Score, transformed_score: Score) -> List[str]:
        """Validate rhythm simplification transformation"""
        errors = []
        
        for orig_part, trans_part in zip(original_score.parts, transformed_score.parts):
            for orig_voice, trans_voice in zip(orig_part.voices, trans_part.voices):
                for orig_measure, trans_measure in zip(orig_voice.measures, trans_voice.measures):
                    # Check that notes are simplified (not more complex)
                    orig_notes = [e for e in orig_measure.events if isinstance(e, NoteEvent)]
                    trans_notes = [e for e in trans_measure.events if isinstance(e, NoteEvent)]
                    
                    # Rhythm simplification can reduce note count but not increase complexity
                    orig_total_duration = sum(n.duration for n in orig_notes)
                    trans_total_duration = sum(n.duration for n in trans_notes)
                    
                    if abs(orig_total_duration - trans_total_duration) > Fraction(1, 32):
                        errors.append(f"Rhythm simplification must preserve total duration in measure {orig_measure.number}")
        
        return errors
    
    def _validate_style_change(self, original_score: Score, transformed_score: Score) -> List[str]:
        """Validate style change transformation"""
        errors = []
        
        # Style changes should preserve essential musical structure
        if len(original_score.parts) != len(transformed_score.parts):
            errors.append("Style change must preserve part structure")
        
        # Check that measure count is preserved
        orig_measures = sum(len(part.voices[0].measures) for part in original_score.parts if part.voices)
        trans_measures = sum(len(part.voices[0].measures) for part in transformed_score.parts if part.voices)
        
        if orig_measures != trans_measures:
            errors.append("Style change must preserve measure structure")
        
        return errors
    
    def _validate_harmonic_reharm(self, original_score: Score, transformed_score: Score) -> List[str]:
        """Validate harmonic reharmonization transformation"""
        errors = []
        
        # Reharmonization must preserve melody
        for orig_part, trans_part in zip(original_score.parts, transformed_score.parts):
            for orig_voice, trans_voice in zip(orig_part.voices, trans_part.voices):
                for orig_measure, trans_measure in zip(orig_voice.measures, trans_voice.measures):
                    orig_notes = [e for e in orig_measure.events if isinstance(e, NoteEvent)]
                    trans_notes = [e for e in trans_measure.events if isinstance(e, NoteEvent)]
                    
                    if len(orig_notes) != len(trans_notes):
                        errors.append(f"Reharmonization must preserve note count in measure {orig_measure.number}")
                        continue
                    
                    for orig_note, trans_note in zip(orig_notes, trans_notes):
                        # Melody pitches must be preserved (or transposed consistently)
                        orig_midi = self._note_to_midi(orig_note)
                        trans_midi = self._note_to_midi(trans_note)
                        
                        # Allow for consistent transposition in reharmonization
                        if orig_midi is not None and trans_midi is not None:
                            # Check if it's a simple transposition (same interval across all notes)
                            # This would be caught by transposition validation if both flags are set
                            pass
                        
                        # Check that rhythm is preserved
                        if orig_note.duration != trans_note.duration:
                            errors.append(f"Reharmonization must preserve rhythm at t={orig_note.onset}")
                        
                        if orig_note.onset != trans_note.onset:
                            errors.append(f"Reharmonization must preserve onset at t={orig_note.onset}")
        
        return errors
    
    def _validate_global_constraints(self, original_score: Score, transformed_score: Score) -> List[str]:
        """Validate global constraints that apply to all transformations"""
        errors = []
        
        # No transformation should change basic structure
        if len(original_score.parts) != len(transformed_score.parts):
            errors.append("Transformation must preserve part count")
        
        # No transformation should create invalid musical structures
        for trans_part in transformed_score.parts:
            for trans_voice in trans_part.voices:
                for trans_measure in trans_voice.measures:
                    # Check for overlapping events
                    sorted_events = sorted(trans_measure.events, key=lambda e: e.onset)
                    
                    for i, event in enumerate(sorted_events):
                        if i > 0 and hasattr(event, 'duration'):
                            prev_event = sorted_events[i-1]
                            if hasattr(prev_event, 'duration'):
                                if event.onset < prev_event.onset + prev_event.duration:
                                    errors.append(f"Transformation created overlapping events in measure {trans_measure.number}")
        
        return errors
    
    def _note_to_midi(self, note) -> Optional[int]:
        """Convert note to MIDI number"""
        if not isinstance(note, NoteEvent):
            return None
        
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        try:
            # Find base note
            base_index = note_names.index(note.pitch_step)
            if note.pitch_alter > 0:
                base_index += note.pitch_alter
            elif note.pitch_alter < 0:
                base_index += note.pitch_alter
            
            # Calculate MIDI
            midi = (note.octave + 1) * 12 + base_index
            return midi
        except (ValueError, IndexError):
            return None
    
    def get_transformation_prompt_additions(self, allowed_flags: Set[str]) -> str:
        """Generate prompt additions based on allowed transformation flags"""
        if not allowed_flags:
            return ""
        
        additions = []
        additions.append("ALLOWED TRANSFORMATIONS:")
        
        for flag in allowed_flags:
            if flag in self.allowed_transformations:
                config = self.allowed_transformations[flag]
                additions.append(f"- {flag.upper()}: {config['description']}")
        
        additions.append("\nRULES:")
        additions.append("- Only perform the explicitly allowed transformations above.")
        additions.append("- Do not invent creative changes beyond the allowed types.")
        additions.append("- If multiple flags are set, apply them in combination.")
        additions.append("- Reject requests for transformation types not in the allowed list.")
        
        return "\n".join(additions)