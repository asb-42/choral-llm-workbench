from typing import Dict, List, Tuple, Optional
from ikr_light import Score, Part, Voice, Measure, NoteEvent, RestEvent, HarmonyEvent, LyricEvent


class HelmholtzConverter:
    """Convert IKR events to Helmholtz notation (read-only view)"""
    
    def __init__(self):
        # SPN to Helmholtz mapping (C4 = c', B3 = b)
        self.spn_to_helmholtz = {
            'C': {0: 'C,,,,', 1: 'C,,,', 2: 'C,,', 3: 'C,', 4: 'c', 5: "c'", 6: "c''", 7: "c'''", 8: "c''''"},
            'D': {0: 'D,,,,', 1: 'D,,,', 2: 'D,,', 3: 'D,', 4: 'd', 5: "d'", 6: "d''", 7: "d'''", 8: "d''''"},
            'E': {0: 'E,,,,', 1: 'E,,,', 2: 'E,,', 3: 'E,', 4: 'e', 5: "e'", 6: "e''", 7: "e'''", 8: "e''''"},
            'F': {0: 'F,,,,', 1: 'F,,,', 2: 'F,,', 3: 'F,', 4: 'f', 5: "f'", 6: "f''", 7: "f'''", 8: "f''''"},
            'G': {0: 'G,,,,', 1: 'G,,,', 2: 'G,,', 3: 'G,', 4: 'g', 5: "g'", 6: "g''", 7: "g'''", 8: "g''''"},
            'A': {0: 'A,,,,', 1: 'A,,,', 2: 'A,,', 3: 'A,', 4: 'a', 5: "a'", 6: "a''", 7: "a'''", 8: "a''''"},
            'B': {0: 'B,,,,', 1: 'B,,,', 2: 'B,,', 3: 'B,', 4: 'b', 5: "b'", 6: "b''", 7: "b'''", 8: "b''''"},
        }
        
        # Note: B in German notation is B natural, H is B natural
        # For English B, we need to handle carefully
        # In Helmholtz: B-flat = 'b', B-natural = 'h' (German), 
        # But we'll use English convention: B-flat = '♭', B-natural = 'b'
    
    def note_to_helmholtz(self, note_event: NoteEvent) -> str:
        """Convert a single note event to Helmholtz notation"""
        base_note = note_event.pitch_step
        
        # Handle B special case (English B = German H, B-flat = German B)
        if base_note == 'B':
            if note_event.pitch_alter == -1:  # B-flat
                # In Helmholtz, B-flat is 'b' (lowercase)
                helmholtz_base = 'b'
            else:
                # B-natural is 'h' in German, but we'll use 'b' for clarity
                # and add natural sign if needed
                helmholtz_base = 'b♮'
        else:
            # Get base Helmholtz note
            helmholtz_base = self.spn_to_helmholtz.get(base_note, {}).get(note_event.octave, base_note.lower())
        
        # Add accidentals
        if note_event.pitch_alter == 1:
            helmholtz_base += '♯'
        elif note_event.pitch_alter == -1:
            if base_note != 'B':  # B-flat already handled
                helmholtz_base += '♭'
        elif note_event.pitch_alter == 2:
            helmholtz_base += '𝄪'
        elif note_event.pitch_alter == -2:
            helmholtz_base += '𝄫'
        
        # Add tie information
        tie_suffix = ""
        if note_event.tie:
            if note_event.tie == "start":
                tie_suffix = "～"
            elif note_event.tie == "stop":
                tie_suffix = "～"
        
        return helmholtz_base + tie_suffix
    
    def duration_to_helmholtz_text(self, duration) -> str:
        """Convert duration fraction to readable text"""
        # Convert to simplified fraction for display
        from fractions import Fraction
        
        if duration == Fraction(1, 4):
            return "quarter"
        elif duration == Fraction(1, 2):
            return "half"
        elif duration == Fraction(1, 1):
            return "whole"
        elif duration == Fraction(1, 8):
            return "eighth"
        elif duration == Fraction(1, 16):
            return "sixteenth"
        elif duration == Fraction(3, 4):
            return "dotted half"
        elif duration == Fraction(3, 8):
            return "dotted quarter"
        elif duration == Fraction(3, 16):
            return "dotted eighth"
        else:
            return str(duration)
    
    def score_to_helmholtz_tlr(self, score: Score) -> str:
        """Convert IKR score to TLR format with Helmholtz notation"""
        lines = []
        
        # Sort parts by name for deterministic output
        sorted_parts = sorted(score.parts, key=lambda p: p.name)
        
        for part in sorted_parts:
            lines.append(f"PART {part.name} ROLE {part.role}")
            
            # Sort voices by ID for deterministic output
            sorted_voices = sorted(part.voices, key=lambda v: v.id)
            
            for voice in sorted_voices:
                lines.append(f"VOICE {voice.id}")
                
                # Sort measures by number for deterministic output
                sorted_measures = sorted(voice.measures, key=lambda m: m.number)
                
                for measure in sorted_measures:
                    lines.append(f"MEASURE {measure.number} TIME {measure.time_signature}")
                    
                    # Sort events by onset for deterministic output
                    sorted_events = sorted(measure.events, key=lambda e: e.onset)
                    
                    for event in sorted_events:
                        line = self._event_to_helmholtz_tlr(event)
                        if line:
                            lines.append(line)
                    
                    lines.append("")  # Empty line after measure
        
        return "\n".join(lines).strip()
    
    def _event_to_helmholtz_tlr(self, event) -> str:
        """Convert single event to TLR line with Helmholtz notation"""
        if isinstance(event, NoteEvent):
            helmholtz_note = self.note_to_helmholtz(event)
            duration_text = self.duration_to_helmholtz_text(event.duration)
            return f"NOTE t={event.onset} dur={event.duration} pitch={helmholtz_note} ({duration_text})"
        
        elif isinstance(event, RestEvent):
            duration_text = self.duration_to_helmholtz_text(event.duration)
            return f"REST t={event.onset} dur={event.duration} ({duration_text})"
        
        elif isinstance(event, HarmonyEvent):
            return f"HARMONY t={event.onset} symbol={event.harmony}"
        
        elif isinstance(event, LyricEvent):
            return f"LYRIC t={event.onset} text={event.text}"
        
        return ""
    
    def get_dual_notation_display(self, score: Score) -> Dict[str, str]:
        """Get both SPN and Helmholtz notation displays"""
        spn_tlr = ""
        
        # Generate SPN TLR (original format)
        from tlr_converter import TLRConverter
        tlr_converter = TLRConverter()
        spn_tlr = tlr_converter.ikr_to_tlr(score)
        
        # Generate Helmholtz TLR
        helmholtz_tlr = self.score_to_helmholtz_tlr(score)
        
        return {
            "spn": spn_tlr,
            "helmholtz": helmholtz_tlr
        }
    
    def create_side_by_side_comparison(self, score: Score) -> str:
        """Create side-by-side comparison of SPN and Helmholtz"""
        dual = self.get_dual_notation_display(score)
        
        lines = []
        lines.append("=" * 80)
        lines.append("DUAL NOTATION DISPLAY: SPN (left) | HELMHOLTZ (right)")
        lines.append("=" * 80)
        
        spn_lines = dual["spn"].split('\n')
        helmholtz_lines = dual["helmholtz"].split('\n')
        
        # Pad shorter list
        max_lines = max(len(spn_lines), len(helmholtz_lines))
        spn_lines.extend([""] * (max_lines - len(spn_lines)))
        helmholtz_lines.extend([""] * (max_lines - len(helmholtz_lines)))
        
        for spn_line, helmholtz_line in zip(spn_lines, helmholtz_lines):
            # Format side by side
            spn_part = spn_line.ljust(38)
            helmholtz_part = helmholtz_line.ljust(38)
            lines.append(f"{spn_part} | {helmholtz_part}")
        
        return "\n".join(lines)