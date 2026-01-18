from dataclasses import dataclass
from typing import List, Tuple, Optional
from ikr_light import Score, Part, Voice, Measure, Event, NoteEvent, HarmonyEvent, RestEvent, LyricEvent


@dataclass
class SemanticDiffEntry:
    """Represents a single semantic difference in musical transformation"""
    scope: str           # "score", "part", "voice", "measure", "note"
    location: str        # e.g. "Soprano, Measure 12"
    change_type: str     # "rhythm", "pitch", "harmony", "style", "structure"
    description: str     # Human-readable explanation of the change
    before_value: str = None
    after_value: str = None


class SemanticDiffAnalyzer:
    """Analyzes musical differences at semantic level"""
    
    def __init__(self):
        pass
    
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
        diffs.extend(note_diffs)
        
        # 3. Harmony changes
        harmony_diffs = self._analyze_harmony_changes(ikr_before, ikr_after)
        diffs.extend(harmony_diffs)
        
        # 4. Rhythm changes
        rhythm_diffs = self._analyze_rhythm_changes(ikr_before, ikr_after)
        diffs.extend(rhythm_diffs)
        
        # 5. Style changes
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
                diffs.append(SemanticDiffEntry(
                    scope="harmony",
                    location=location,
                    change_type="harmony",
                    description=f"Added harmony: {after_harm.harmony}"
                ))
            elif after_harm is None:
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
            return {
                "type": "pitch",
                "desc": f"Pitch changed: {self._format_note(before)} → {self._format_note(after)}",
                "before": self._format_note(before),
                "after": self._format_note(after)
            }
        elif not pitch_changed and duration_changed:
            return {
                "type": "rhythm",
                "desc": f"Duration changed: {before.duration} → {after.duration}",
                "before": str(before.duration),
                "after": str(after.duration)
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
    
    def _sort_by_importance(self, diff: SemanticDiffEntry) -> Tuple:
        """Sort diffs by scope importance"""
        scope_order = {"score": 0, "part": 1, "voice": 2, "measure": 3, "note": 4, "harmony": 5, "rhythm": 6}
        return (
            scope_order.get(diff.scope, 10),  # Default high number for unknown scopes
            diff.location or "",
            diff.change_type or "",
            diff.description or ""
        )