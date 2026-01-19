from dataclasses import dataclass
from typing import List, Tuple, Optional
from ikr_light import Score, Part, Voice, Measure, Event, NoteEvent, HarmonyEvent, RestEvent, LyricEvent
from fractions import Fraction


@dataclass
class SemanticDiffEntry:
    """Represents a single semantic difference in musical transformation"""
    scope: str           # "score", "part", "voice", "measure", "note"
    location: str        # e.g. "Soprano, Measure 12"
    change_type: str     # "rhythm", "pitch", "harmony", "style", "structure"
    description: str     # Human-readable explanation of the change
    before_value: Optional[str] = None
    after_value: Optional[str] = None


class SemanticDiffAnalyzer:
    """Analyzes musical differences at semantic level"""
    
    def __init__(self):
        pass
    
    def _duration_to_note_name(self, duration) -> str:
        """Convert duration Fraction to musical note name"""
        if not duration:
            return "unknown duration"
        
        # Handle negative durations (shouldn't happen but be defensive)
        if duration < 0:
            duration = -duration
        
        # Common note durations
        if duration == Fraction(1, 1):
            return "whole note"
        elif duration == Fraction(1, 2):
            return "half note"
        elif duration == Fraction(1, 4):
            return "quarter note"
        elif duration == Fraction(1, 8):
            return "eighth note"
        elif duration == Fraction(1, 16):
            return "sixteenth note"
        elif duration == Fraction(3, 4):
            return "dotted whole note"
        elif duration == Fraction(3, 8):
            return "dotted half note"
        elif duration == Fraction(3, 16):
            return "dotted quarter note"
        elif duration == Fraction(3, 32):
            return "dotted eighth note"
        elif duration == Fraction(7, 8):
            return "double dotted half note"
        elif duration == Fraction(7, 16):
            return "double dotted quarter note"
        else:
            # For complex durations, provide decimal approximation with context
            decimal_val = float(duration)
            if decimal_val < 0.25:
                return f"short note ({duration})"
            elif decimal_val > 2:
                return f"long note ({duration})"
            else:
                return f"note duration {duration}"
    
    def _analyze_pitch_change_with_interval(self, before: NoteEvent, after: NoteEvent) -> dict:
        """Analyze pitch change with interval and octave information"""
        # Pitch step to MIDI conversion
        pitch_to_midi = {
            'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
        }
        
        # Convert pitches to MIDI values
        try:
            before_midi = 12 * before.octave + pitch_to_midi.get(before.pitch_step, 0) + (before.pitch_alter or 0)
            after_midi = 12 * after.octave + pitch_to_midi.get(after.pitch_step, 0) + (after.pitch_alter or 0)
        except (AttributeError, TypeError):
            # Fallback if pitch_step not available
            return {
                'interval_type': 'unknown',
                'semitones': 0,
                'octaves': 0,
                'direction': 'no change'
            }
        
        # Calculate interval
        midi_diff = after_midi - before_midi
        semitones = midi_diff % 12
        octaves = (midi_diff // 12)
        
        # Interval names
        interval_names = {
            0: "unison", 1: "minor second", 2: "major second", 3: "minor third",
            4: "major third", 5: "perfect fourth", 6: "tritone", 7: "perfect fifth",
            8: "minor sixth", 9: "major sixth", 10: "minor seventh", 11: "major seventh"
        }
        
        direction = "up" if midi_diff > 0 else "down" if midi_diff < 0 else "no change"
        interval_name = interval_names.get(abs(semitones), f"{abs(semitones)} semitones")
        
        return {
            'interval_type': interval_name,
            'semitones': semitones,
            'octaves': octaves,
            'direction': direction,
            'absolute_semitones': abs(midi_diff)
        }
    
    def _detect_transposition(self, pitch_changes: List[SemanticDiffEntry]) -> Optional[dict]:
        """Detect if pitch changes form a consistent transposition"""
        if len(pitch_changes) < 3:  # Need minimum notes for pattern
            return None
        
        # Extract semitone differences
        semitone_diffs = []
        for change in pitch_changes:
            # Convert desc back to semitones (simplified approach)
            desc = change.description
            if 'semitones' in desc:
                try:
                    semitones = int(desc.split('(')[-1].split(' semitones')[0])
                    semitone_diffs.append(semitones)
                except (ValueError, IndexError):
                    pass
        
        if len(semitone_diffs) < 3:
            return None
        
        # Check if all differences are the same (consistent transposition)
        if len(set(semitone_diffs)) != 1:
            return None
        
        consistent_semitones = semitone_diffs[0]
        
        # Determine interval name
        interval_names = {
            1: "minor second", 2: "major second", 3: "minor third",
            4: "major third", 5: "perfect fourth", 6: "tritone", 7: "perfect fifth",
            8: "minor sixth", 9: "major sixth", 10: "minor seventh", 11: "major seventh"
        }
        
        direction = "up" if consistent_semitones > 0 else "down" if consistent_semitones < 0 else "no change"
        abs_semitones = abs(consistent_semitones)
        interval_name = interval_names.get(abs_semitones % 12, f"{abs_semitones} semitones")
        
        return {
            'is_transposition': True,
            'semitones': consistent_semitones,
            'direction': direction,
            'interval_name': interval_name,
            'absolute_semitones': abs(semitones)
        }
    
    def _analyze_key_changes(self, before: Score, after: Score) -> List[SemanticDiffEntry]:
        """Analyze key/tonality changes between scores"""
        diffs = []
        
        # Extract key information from metadata if available
        before_key = before.metadata.get('key', 'unknown') if before and before.metadata else 'unknown'
        after_key = after.metadata.get('key', 'unknown') if after and after.metadata else 'unknown'
        
        # If metadata not available, try to infer from notes (simplified)
        if before_key == 'unknown' or after_key == 'unknown':
            before_key = self._infer_key_from_notes(before)
            after_key = self._infer_key_from_notes(after)
        
        # Compare keys
        if before_key != after_key:
            # Determine if this is a transposition
            is_transposition = self._is_transposition_of_key(before_key, after_key)
            
            if is_transposition:
                interval = self._get_key_interval(before_key, after_key)
                direction = "up" if interval > 0 else "down" if interval < 0 else "no change"
                abs_interval = abs(interval)
                
                interval_names = {1: "minor second", 2: "major second", 3: "minor third",
                               4: "major third", 5: "perfect fourth", 6: "tritone", 7: "perfect fifth",
                               8: "minor sixth", 9: "major sixth", 10: "minor seventh", 11: "major seventh"}
                
                interval_name = interval_names.get(abs_interval % 12, f"{abs_interval} semitones")
                
                diffs.append(SemanticDiffEntry(
                    scope="score",
                    location="Tonality",
                    change_type="transposition",
                    description=f"Key transposed {direction} by {interval_name} ({abs_interval} semitones)",
                    before_value=before_key,
                    after_value=after_key
                ))
            else:
                # Explicit key change (not a simple transposition)
                diffs.append(SemanticDiffEntry(
                    scope="score",
                    location="Tonality",
                    change_type="key_change",
                    description=f"Key changed: {before_key} → {after_key}",
                    before_value=before_key,
                    after_value=after_key
                ))
        
        # Sort by hierarchical importance: score -> part -> voice -> measure -> note
        diffs.sort(key=self._sort_by_importance)
        
        return diffs
    
    def _infer_key_from_notes(self, score: Score) -> str:
        """Simplified key inference from note patterns (heuristic)"""
        if not score or not score.parts:
            return "unknown"
        
        # Get first few notes from first voice of first part
        for part in score.parts:
            if part.voices:
                voice = part.voices[0]
                if voice.measures:
                    for measure in voice.measures[:3]:  # First 3 measures
                        for event in measure.events[:5]:  # First 5 notes
                            if isinstance(event, NoteEvent):
                                # Very basic key inference from pitch classes
                                pitch_class = event.pitch_step
                                if pitch_class in ['C', 'G']:
                                    if pitch_class == 'C':
                                        # Check for C major vs C minor by looking at E/Eb
                                        for check_event in measure.events[:10]:
                                            if isinstance(check_event, NoteEvent):
                                                if check_event.pitch_step == 'E':
                                                    return "C major"
                                                elif check_event.pitch_step == 'Eb' or check_event.pitch_step == 'D#':
                                                    return "C minor"
                                elif pitch_class == 'G':
                                    # Check for G major vs G minor by looking at B/Bb
                                    for check_event in measure.events[:10]:
                                        if isinstance(check_event, NoteEvent):
                                            if check_event.pitch_step == 'B':
                                                return "G major"
                                            elif check_event.pitch_step == 'Bb' or check_event.pitch_step == 'A#':
                                                return "G minor"
                        
                        # Default to major based on most common
                        return f"{pitch_class} major"
        
        return "unknown"
    
    def _is_transposition_of_key(self, before_key: str, after_key: str) -> bool:
        """Check if key change is a transposition"""
        if not before_key or not after_key:
            return False
        
        # Extract pitch class from keys
        before_class = self._extract_pitch_class(before_key)
        after_class = self._extract_pitch_class(after_key)
        
        before_class = extract_pitch_class(before_key)
        after_class = extract_pitch_class(after_key)
        
        # If pitch class is the same and both have same mode (major/minor), likely transposition
        return (before_class == after_class and 
                ('major' in before_key) == ('major' in after_key) and
                ('minor' in before_key) == ('minor' in after_key))
    
    def _get_key_interval(self, before_key: str, after_key: str) -> int:
        """Calculate semitone interval between keys"""
        # Note: This is a simplified implementation
        key_to_semitone = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5,
            'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }
        
        before_class = before_key.split()[0] if before_key else 'C'
        after_class = after_key.split()[0] if after_key else 'C'
        
        before_semitone = key_to_semitone.get(before_class, 0)
        after_semitone = key_to_semitone.get(after_class, 0)
        
        return after_semitone - before_semitone
    
    def _analyze_meter_changes(self, before: Score, after: Score) -> List[SemanticDiffEntry]:
        """Analyze meter/time signature changes between scores"""
        diffs = []
        
        # Extract time signatures from all measures
        before_meters = self._extract_time_signatures(before)
        after_meters = self._extract_time_signatures(after)
        
        # Find changes
        all_locations = set(before_meters.keys()) | set(after_meters.keys())
        
        for location in all_locations:
            before_meter = before_meters.get(location)
            after_meter = after_meters.get(location)
            
            if before_meter != after_meter:
                # Parse time signatures
                before_top, before_bottom = self._parse_time_signature(before_meter)
                after_top, after_bottom = self._parse_time_signature(after_meter)
                
                if before_top == after_top and before_bottom == after_bottom:
                    continue  # No actual change
                
                # Determine type of change
                is_simple_before = before_bottom in [2, 4] and before_top <= 4
                is_simple_after = after_bottom in [2, 4] and after_top <= 4
                before_is_even = before_bottom % 2 == 0
                after_is_even = after_bottom % 2 == 0
                
                if before_top == after_top:
                    # Same top number, only bottom changed
                    if before_is_even and not after_is_even:
                        change_type = "even_to_odd"
                        description = f"Time signature: {before_meter} (even) → {after_meter} (odd)"
                    elif not before_is_even and after_is_even:
                        change_type = "odd_to_even"
                        description = f"Time signature: {before_meter} (odd) → {after_meter} (even)"
                    else:
                        change_type = "subdivision_change"
                        description = f"Time signature: {before_meter} → {after_meter}"
                elif before_bottom == after_bottom:
                    # Same bottom number, only top changed
                    if before_top > after_top:
                        change_type = "simplification"
                        description = f"Meter simplified: {before_top}/{before_bottom} → {after_top}/{after_bottom}"
                    elif before_top < after_top:
                        change_type = "complexification"
                        description = f"Meter complexified: {before_top}/{before_bottom} → {after_top}/{after_bottom}"
                else:
                    # Both changed
                    change_type = "complete_change"
                    description = f"Time signature: {before_meter} → {after_meter}"
                
                diffs.append(SemanticDiffEntry(
                    scope="measure",
                    location=location,
                    change_type="meter_change",
                    description=description,
                    before_value=before_meter,
                    after_value=after_meter
                ))
        
        return diffs
    
    def _extract_time_signatures(self, score: Score) -> dict:
        """Extract time signatures from all measures"""
        meters = {}
        
        if not score or not score.parts:
            return meters
        
        for part in score.parts:
            for voice in part.voices:
                for measure in voice.measures:
                    if measure.time_signature:
                        location = f"{part.name}, Voice {voice.id}, Measure {measure.number}"
                        meters[location] = measure.time_signature
        
        return meters
    
    def _parse_time_signature(self, time_sig: str) -> Tuple[int, int]:
        """Parse time signature string to (top, bottom) tuple"""
        if not time_sig:
            return 4, 4  # Default to 4/4
        
        parts = time_sig.split('/')
        if len(parts) == 2:
            try:
                top = int(parts[0])
                bottom = int(parts[1])
                return top, bottom
            except ValueError:
                pass
        
        return 4, 4  # Default fallback
    
    def _analyze_style_changes(self, before: Score, after: Score) -> List[SemanticDiffEntry]:
        """Analyze style changes between scores"""
        diffs = []
        
        # Get style classification for both scores
        before_style = self._classify_score_style(before)
        after_style = self._classify_score_style(after)
        
        if before_style != after_style:
            # Determine if this is an improvement
            style_improvement = self._get_style_improvement(before_style, after_style)
            
            if style_improvement:
                change_type = "style_improvement"
                description = f"Style enhanced: {before_style} → {after_style} ({style_improvement})"
            else:
                change_type = "style_change"
                description = f"Style changed: {before_style} → {after_style}"
            
            diffs.append(SemanticDiffEntry(
                scope="score",
                location="Style",
                change_type=change_type,
                description=description,
                before_value=before_style,
                after_value=after_style
            ))
        
        return diffs
    
    def _classify_score_style(self, score: Score) -> str:
        """Classify musical style based on harmonic and melodic characteristics"""
        if not score or not score.parts:
            return "unknown"
        
        # Analyze characteristics
        total_notes = 0
        harmony_events = 0
        unique_pitches = set()
        rhythmic_complexity = 0
        
        for part in score.parts:
            for voice in part.voices:
                for measure in voice.measures:
                    for event in measure.events:
                        if isinstance(event, NoteEvent):
                            total_notes += 1
                            unique_pitches.add(f"{event.pitch_step}{event.octave}")
                            # Calculate rhythmic complexity
                            if event.duration == Fraction(1, 8):  # Eighth notes
                                rhythmic_complexity += 1
                            elif event.duration == Fraction(1, 16):  # Sixteenth notes
                                rhythmic_complexity += 2
                            elif event.duration < Fraction(1, 8):  # Smaller divisions
                                rhythmic_complexity += 3
                        elif isinstance(event, HarmonyEvent):
                            harmony_events += 1
        
        # Style classification logic
        if total_notes == 0:
            return "empty"
        
        # Calculate ratios
        harmony_ratio = harmony_events / total_notes if total_notes > 0 else 0
        pitch_diversity = len(unique_pitches) / total_notes if total_notes > 0 else 0
        avg_rhythmic_complexity = rhythmic_complexity / total_notes if total_notes > 0 else 0
        
        # Classify based on characteristics
        if harmony_ratio > 0.4:  # Rich harmony
            if avg_rhythmic_complexity > 1.5:  # Complex rhythm
                if pitch_diversity > 0.7:
                    return "contemporary jazz"
                else:
                    return "romantic"
            elif avg_rhythmic_complexity > 0.5:
                if pitch_diversity > 0.5:
                    return "classical"
                else:
                    return "folk"
            else:
                return "baroque"
        elif harmony_ratio > 0.2:
            if avg_rhythmic_complexity > 1.0:
                return "renaissance"
            else:
                return "minimalist"
        elif pitch_diversity > 0.8:
            return "modern experimental"
        elif avg_rhythmic_complexity > 1.2:
            return "progressive"
        else:
            return "traditional"
    
    def _parse_time_signature(self, time_sig: str) -> Tuple[int, int]:
        """Parse time signature string to (top, bottom) tuple"""
        if not time_sig:
            return 4, 4  # Default to 4/4
        
        parts = time_sig.split('/')
        if len(parts) == 2:
            try:
                top = int(parts[0])
                bottom = int(parts[1])
                return top, bottom
            except ValueError:
                pass
        
        return 4, 4  # Default fallback
    
    def _get_style_improvement(self, before_style: str, after_style: str) -> Optional[str]:
        """Determine if style change represents an improvement"""
        # Subjective assessment of style improvements
        style_hierarchy = {
            'minimalist': ['traditional', 'folk'],
            'traditional': ['contemporary jazz', 'romantic'],
            'folk': ['renaissance', 'minimalist'],
            'renaissance': ['baroque', 'traditional'],
            'baroque': ['classical', 'romantic'],
            'classical': ['contemporary jazz', 'progressive'],
            'romantic': ['contemporary jazz'],
            'modern experimental': ['progressive', 'classical']
        }
        
        # Check if improvement
        if before_style in style_hierarchy.get(after_style, []):
            return style_hierarchy[after_style][0] if style_hierarchy.get(after_style) else None
        
        return None
    
    def compute_semantic_diff(
        self, 
        ikr_before: Score, 
        ikr_after: Score
    ) -> List[SemanticDiffEntry]:
        """
        Compute semantic differences between two IKR scores
        
        Returns sorted list of semantic differences
        """
        diffs = []
        
        # 1. Structure-level changes (parts, voices, measures)
        structure_diffs = self._analyze_structure_changes(ikr_before, ikr_after)
        diffs.extend(structure_diffs)
        
        # 2. Note-level changes
        note_diffs = self._analyze_note_changes(ikr_before, ikr_after)
        
        # 2a. Check for transposition and group if detected
        pitch_changes = [diff for diff in note_diffs if diff.change_type == 'pitch']
        if pitch_changes:
            transposition_info = self._detect_transposition(pitch_changes)
            if transposition_info and transposition_info['is_transposition']:
                # Create grouped transposition entry
                transposition_entry = SemanticDiffEntry(
                    scope="score",
                    location="Transposition",
                    change_type="transposition",
                    description=f"Transposed {transposition_info['direction']} by {transposition_info['interval_name']} ({transposition_info['absolute_semitones']} semitones)",
                    before_value=f"{transposition_info['note_count']} notes",
                    after_value=f"transposed by {transposition_info['absolute_semitones']} semitones"
                )
                
                # Add transposition entry instead of individual pitch changes
                diffs.append(transposition_entry)
                # Filter out individual pitch changes that were grouped
                note_diffs = [diff for diff in note_diffs if diff not in pitch_changes]
            else:
                # No transposition detected, add individual changes
                diffs.extend(note_diffs)
        else:
            # No pitch changes, add all note changes
            diffs.extend(note_diffs)
        
        # 3. Harmony changes
        harmony_diffs = self._analyze_harmony_changes(ikr_before, ikr_after)
        diffs.extend(harmony_diffs)
        
        # 4. Key/Tonality changes
        key_diffs = self._analyze_key_changes(ikr_before, ikr_after)
        diffs.extend(key_diffs)
        
        # 5. Meter/Time Signature changes
        meter_diffs = self._analyze_meter_changes(ikr_before, ikr_after)
        diffs.extend(meter_diffs)
        
        # 6. Rhythm changes
        rhythm_diffs = self._analyze_rhythm_changes(ikr_before, ikr_after)
        diffs.extend(rhythm_diffs)
        
        # 7. Style changes
        style_diffs = self._analyze_style_changes(ikr_before, ikr_after)
        diffs.extend(style_diffs)
        
        # Sort by hierarchical importance: score -> part -> voice -> measure -> note
        diffs.sort(key=self._sort_by_importance)
        
        return diffs
    
    def _analyze_structure_changes(self, before: Score, after: Score) -> List[SemanticDiffEntry]:
        """Analyze changes in overall score structure"""
        diffs = []
        
        # Check for added/removed parts
        before_parts = {part.id: part for part in before.parts}
        after_parts = {part.id: part for part in after.parts}
        
        added_part_ids = set(after_parts.keys()) - set(before_parts.keys())
        removed_part_ids = set(before_parts.keys()) - set(after_parts.keys())
        
        for part_id in added_part_ids:
            diffs.append(SemanticDiffEntry(
                scope="score",
                location=f"Part {part_id}",
                change_type="structure",
                description=f"Added part: {after_parts[part_id].name}"
            ))
        
        for part_id in removed_part_ids:
            diffs.append(SemanticDiffEntry(
                scope="score",
                location=f"Part {part_id}",
                change_type="structure",
                description=f"Removed part: {before_parts[part_id].name}"
            ))
        
        return diffs
    
    def _analyze_note_changes(self, before: Score, after: Score) -> List[SemanticDiffEntry]:
        """Analyze changes in individual notes"""
        diffs = []
        
        # Create event maps for efficient comparison
        before_events = {}
        after_events = {}
        
        for part in before.parts:
            for voice in part.voices:
                for measure in voice.measures:
                    for event in measure.events:
                        if isinstance(event, NoteEvent):
                            key = (part.id, voice.id, measure.number, event.onset)
                            before_events[key] = event
        
        for part in after.parts:
            for voice in part.voices:
                for measure in voice.measures:
                    for event in measure.events:
                        if isinstance(event, NoteEvent):
                            key = (part.id, voice.id, measure.number, event.onset)
                            after_events[key] = event
        
        # Find changes
        all_keys = set(before_events.keys()) | set(after_events.keys())
        
        for key in all_keys:
            before_event = before_events.get(key)
            after_event = after_events.get(key)
            
            if before_event is None:
                # Note added
                diffs.append(SemanticDiffEntry(
                    scope="note",
                    location=f"{key[0]}, {key[1]}, Measure {key[2]}, Beat {key[3]}",
                    change_type="pitch",
                    description=f"Added note: {self._format_note(after_event)}"
                ))
            elif after_event is None:
                # Note removed
                diffs.append(SemanticDiffEntry(
                    scope="note",
                    location=f"{key[0]}, {key[1]}, Measure {key[2]}, Beat {key[3]}",
                    change_type="pitch",
                    description=f"Removed note: {self._format_note(before_event)}"
                ))
            else:
                # Note changed
                change_desc = self._analyze_note_change(before_event, after_event)
                if change_desc:
                    diffs.append(SemanticDiffEntry(
                        scope="note",
                        location=f"{key[0]}, {key[1]}, Measure {key[2]}, Beat {key[3]}",
                        change_type=change_desc["type"],
                        description=change_desc["desc"],
                        before_value=change_desc["before"],
                        after_value=change_desc["after"]
                    ))
        
        return diffs
    
    def _analyze_harmony_changes(self, before: Score, after: Score) -> List[SemanticDiffEntry]:
        """Analyze harmonic changes"""
        diffs = []
        
        # Extract harmony events
        before_harmonies = self._extract_harmonies(before)
        after_harmonies = self._extract_harmonies(after)
        
        # Compare harmonies by location
        all_locations = set(before_harmonies.keys()) | set(after_harmonies.keys())
        
        for location in all_locations:
            before_harm = before_harmonies.get(location)
            after_harm = after_harmonies.get(location)
            
            if before_harm is None:
                if after_harm:
                    diffs.append(SemanticDiffEntry(
                        scope="harmony",
                        location=location,
                        change_type="harmony",
                        description=f"Added harmony: {after_harm.harmony}"
                    ))
            elif after_harm is None:
                if before_harm:
                    diffs.append(SemanticDiffEntry(
                        scope="harmony",
                        location=location,
                        change_type="harmony",
                        description=f"Removed harmony: {before_harm.harmony}"
                    ))
            elif before_harm.harmony != after_harm.harmony:
                diffs.append(SemanticDiffEntry(
                    scope="harmony",
                    location=location,
                    change_type="harmony",
                    description=f"Harmony changed: {before_harm.harmony} → {after_harm.harmony}",
                    before_value=before_harm.harmony,
                    after_value=after_harm.harmony
                ))
        
        return diffs
    
    def _analyze_rhythm_changes(self, before: Score, after: Score) -> List[SemanticDiffEntry]:
        """Analyze rhythmic changes"""
        diffs = []
        
        # Compare note durations and groupings
        before_rhythms = self._extract_rhythms(before)
        after_rhythms = self._extract_rhythms(after)
        
        for location in set(before_rhythms.keys()) | set(after_rhythms.keys()):
            before_rhythm = before_rhythms.get(location)
            after_rhythm = after_rhythms.get(location)
            
            if before_rhythm and after_rhythm:
                before_pattern = self._simplify_rhythm_pattern(before_rhythm)
                after_pattern = self._simplify_rhythm_pattern(after_rhythm)
                
                if before_pattern != after_pattern:
                    diffs.append(SemanticDiffEntry(
                        scope="rhythm",
                        location=location,
                        change_type="rhythm",
                        description=f"Rhythm simplified: {before_pattern} → {after_pattern}",
                        before_value=before_pattern,
                        after_value=after_pattern
                    ))
        
        return diffs
    
    def _analyze_style_changes(self, before: Score, after: Score) -> List[SemanticDiffEntry]:
        """Analyze style changes (high-level heuristics)"""
        diffs = []
        
        # Style heuristics based on overall patterns
        before_style = self._detect_style(before)
        after_style = self._detect_style(after)
        
        if before_style != after_style:
            diffs.append(SemanticDiffEntry(
                scope="score",
                location="Overall",
                change_type="style",
                description=f"Style adapted: {before_style} → {after_style}",
                before_value=before_style,
                after_value=after_style
            ))
        
        return diffs
    
    def _format_note(self, event: NoteEvent) -> str:
        """Format note for display"""
        if not event:
            return "unknown"
            
        # Format pitch from separate components
        alter_symbol = ""
        if event.pitch_alter == 1:
            alter_symbol = "#"
        elif event.pitch_alter == -1:
            alter_symbol = "b"

        pitch = f"{event.pitch_step}{alter_symbol}{event.octave}"
        return f"{pitch} (duration: {event.duration})"
    
    def _analyze_note_change(self, before: NoteEvent, after: NoteEvent) -> Optional[dict]:
        """Analyze what changed between two notes"""
        # Compare pitch components
        before_pitch = (before.pitch_step, before.pitch_alter, before.octave)
        after_pitch = (after.pitch_step, after.pitch_alter, after.octave)

        pitch_changed = before_pitch != after_pitch
        duration_changed = before.duration != after.duration

        if pitch_changed and not duration_changed:
            # Analyze with interval information
            interval_info = self._analyze_pitch_change_with_interval(before, after)
            
            # Format pitch names with accidentals
            def format_pitch(pitch_event):
                if not pitch_event:
                    return "unknown"
                
                name = pitch_event.pitch_step
                octave = pitch_event.octave
                alter = pitch_event.pitch_alter or 0
                
                if alter == 1:
                    name += "#"
                elif alter == -1:
                    name += "b"
                elif alter != 0:
                    name += f"({alter:+})"
                
                return f"{name}{octave}"
            
            before_pitch = format_pitch(before)
            after_pitch = format_pitch(after)
            
            # Create description with interval
            if interval_info['direction'] != 'no change':
                desc = f"Pitch changed: {before_pitch} → {after_pitch} ({interval_info['direction']} {interval_info['interval_type']}, {interval_info['absolute_semitones']} semitones)"
            else:
                desc = f"Pitch changed: {before_pitch} → {after_pitch}"
            
            return {
                "type": "pitch",
                "desc": desc,
                "before": before_pitch,
                "after": after_pitch
            }
        elif not pitch_changed and duration_changed:
            return {
                "type": "rhythm",
                "desc": f"Note duration: {self._duration_to_note_name(before.duration)} → {self._duration_to_note_name(after.duration)}",
                "before": self._duration_to_note_name(before.duration),
                "after": self._duration_to_note_name(after.duration)
            }
        elif pitch_changed and duration_changed:
            return {
                "type": "pitch_rhythm",
                "desc": f"Note changed: {self._format_note(before)} → {self._format_note(after)}",
                "before": self._format_note(before),
                "after": self._format_note(after)
            }
        else:
            return None
    
    def _extract_harmonies(self, score: Score) -> dict:
        """Extract harmony events by location"""
        if not score or not score.parts:
            return {}
            
        harmonies = {}
        for part in score.parts:
            for voice in part.voices:
                for measure in voice.measures:
                    for event in measure.events:
                        if isinstance(event, HarmonyEvent):
                            location = f"{part.name}, Voice {voice.id}, Measure {measure.number}"
                            harmonies[location] = event
        return harmonies
    
    def _extract_rhythms(self, score: Score) -> dict:
        """Extract rhythmic patterns by location"""
        rhythms = {}
        for part in score.parts:
            for voice in part.voices:
                for measure in voice.measures:
                    note_events = [e for e in measure.events if isinstance(e, NoteEvent)]
                    if note_events:
                        location = f"{part.name}, Voice {voice.id}, Measure {measure.number}"
                        rhythms[location] = note_events
        return rhythms
    
    def _simplify_rhythm_pattern(self, notes: List[NoteEvent]) -> str:
        """Simplify rhythmic pattern to basic representation"""
        if not notes:
            return "empty"
        
        durations = [str(note.duration) for note in notes]
        return " + ".join(durations)
    
    def _detect_style(self, score: Score) -> str:
        """Detect musical style based on heuristics"""
        # Simple heuristic based on note density and harmony complexity
        total_events = 0
        harmony_events = 0
        
        for part in score.parts:
            for voice in part.voices:
                for measure in voice.measures:
                    for event in measure.events:
                        total_events += 1
                        if isinstance(event, HarmonyEvent):
                            harmony_events += 1
        
        harmony_ratio = harmony_events / max(1, total_events)
        
        if harmony_ratio > 0.3:
            return "Harmonically rich"
        elif harmony_ratio > 0.1:
            return "Classical"
        else:
            return "Homophonic"
    
    def _group_transformations_by_type(self, diffs: List[SemanticDiffEntry]) -> dict:
        """Group transformations by type for better summary"""
        grouped = {
            'transposition': [],
            'pitch': [],
            'rhythm': [],
            'harmony': [],
            'key': [],
            'meter': [],
            'style': [],
            'structure': []
        }
        
        for diff in diffs:
            change_type = diff.change_type
            if change_type in grouped:
                grouped[change_type].append(diff)
            else:
                # Categorize special types
                if 'transposition' in diff.description.lower():
                    grouped['transposition'].append(diff)
                elif 'key' in diff.description.lower():
                    grouped['key'].append(diff)
                elif 'time signature' in diff.description.lower():
                    grouped['meter'].append(diff)
                elif 'style' in diff.description.lower():
                    grouped['style'].append(diff)
                else:
                    # Default categorization
                    if diff.scope in ['note', 'part', 'voice']:
                        if diff.change_type == 'pitch':
                            grouped['pitch'].append(diff)
                        elif 'rhythm' in diff.description.lower():
                            grouped['rhythm'].append(diff)
                    elif diff.change_type in ['harmony']:
                        grouped['harmony'].append(diff)
                    else:
                        grouped['structure'].append(diff)
        
        return grouped
    
    def create_summary(self, grouped_transforms: dict) -> str:
        """Create a concise summary of transformations"""
        summary_parts = []
        
        # Transposition summary
        if grouped_transforms.get('transposition'):
            trans = grouped_transforms['transposition'][0]
            summary_parts.append(f"Global transposition: {trans['after_value']}")
        
        # Pitch changes summary
        if grouped_transforms.get('pitch'):
            pitch_count = len(grouped_transforms['pitch'])
            summary_parts.append(f"Individual pitch changes: {pitch_count}")
        
        # Rhythm summary
        if grouped_transforms.get('rhythm'):
            rhythm_count = len(grouped_transforms['rhythm'])
            summary_parts.append(f"Rhythmic changes: {rhythm_count}")
        
        # Key/meter changes
        if grouped_transforms.get('key'):
            key_count = len(grouped_transforms['key'])
            summary_parts.append(f"Key changes: {key_count}")
        
        if grouped_transforms.get('meter'):
            meter_count = len(grouped_transforms['meter'])
            summary_parts.append(f"Time signature changes: {meter_count}")
        
        # Style changes
        if grouped_transforms.get('style'):
            style_count = len(grouped_transforms['style'])
            summary_parts.append(f"Style changes: {style_count}")
        
        # Overall count
        total_changes = sum(len(v) for v in grouped_transforms.values())
        summary_parts.append(f"Total transformations: {total_changes}")
        
        if not summary_parts:
            return "No musical changes detected"
        
        return " | ".join(summary_parts)
    
    def _sort_by_importance(self, diff: SemanticDiffEntry) -> Tuple:
        """Sort diffs by scope importance"""
        scope_order = {"score": 0, "part": 1, "voice": 2, "measure": 3, "note": 4, "harmony": 5, "rhythm": 6}
        return (
            scope_order.get(diff.scope, 10),  # Default high number for unknown scopes
            diff.location or "",
            diff.change_type or "",
            diff.description or ""
        )