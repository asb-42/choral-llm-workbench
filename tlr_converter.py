from typing import List, Optional
from fractions import Fraction
from ikr_light import Score, Part, Voice, Measure, Event, NoteEvent, RestEvent, HarmonyEvent, LyricEvent


class TLRConverter:
    """Convert between IKR-light and Textual LLM Representation (TLR)"""
    
    def ikr_to_tlr(self, score: Score) -> str:
        """Convert IKR-light Score to TLR text format"""
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
                        line = self._event_to_tlr(event)
                        if line:
                            lines.append(line)
                    
                    lines.append("")  # Empty line after measure
        
        return "\n".join(lines).strip()
    
    def tlr_to_ikr(self, tlr_text: str) -> Score:
        """Parse TLR text and convert to IKR-light Score"""
        lines = tlr_text.strip().split('\n')
        
        parts = []
        current_part = None
        current_voice = None
        current_measure = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("PART "):
                current_part = self._parse_part_line(line)
                current_voice = None
                current_measure = None
                parts.append(current_part)
            
            elif line.startswith("VOICE ") and current_part:
                current_voice = self._parse_voice_line(line, current_part)
                current_measure = None
                current_part.voices.append(current_voice)
            
            elif line.startswith("MEASURE ") and current_voice:
                current_measure = self._parse_measure_line(line, current_voice)
                current_voice.measures.append(current_measure)
            
            elif current_measure and (line.startswith("NOTE ") or line.startswith("REST ") or 
                                     line.startswith("HARMONY ") or line.startswith("LYRIC ")):
                event = self._parse_event_line(line)
                if event:
                    current_measure.events.append(event)
        
        return Score(metadata={}, parts=parts)
    
    def _event_to_tlr(self, event: Event) -> Optional[str]:
        """Convert single event to TLR line with full explicit values"""
        if isinstance(event, NoteEvent):
            # Always include all attributes explicitly, no defaults
            tie_str = f" tie={event.tie}" if event.tie is not None else ""
            return f"NOTE t={event.onset} dur={event.duration} pitch={event.pitch_step}{event.octave}{self._alter_to_str(event.pitch_alter)}{tie_str}"
        
        elif isinstance(event, RestEvent):
            # Always include both onset and duration explicitly
            return f"REST t={event.onset} dur={event.duration}"
        
        elif isinstance(event, HarmonyEvent):
            # Always include both onset and symbol explicitly
            return f"HARMONY t={event.onset} symbol={event.harmony}"
        
        elif isinstance(event, LyricEvent):
            # Always include both onset and text explicitly
            return f"LYRIC t={event.onset} text={event.text}"
        
        return None
    
    def _alter_to_str(self, alter: int) -> str:
        """Convert pitch alteration to Scientific Pitch Notation string"""
        if alter == 1:
            return "#"
        elif alter == -1:
            return "b"
        elif alter == 0:
            return ""  # Natural - no symbol needed in SPN
        else:
            # Handle double sharps/flats if needed
            if alter == 2:
                return "x"
            elif alter == -2:
                return "bb"
        return ""
    
    def _parse_part_line(self, line: str) -> Part:
        """Parse PART line"""
        parts = line.split()
        name = parts[1]
        role = parts[3] if len(parts) > 3 else "instrument"
        return Part(id=name, name=name, role=role, voices=[])
    
    def _parse_voice_line(self, line: str, part: Part) -> Voice:
        """Parse VOICE line"""
        voice_id = line.split()[1]
        return Voice(id=voice_id, measures=[])
    
    def _parse_measure_line(self, line: str, voice: Voice) -> Measure:
        """Parse MEASURE line"""
        parts = line.split()
        measure_number = int(parts[1])
        time_signature = parts[3] if len(parts) > 3 else "4/4"
        return Measure(number=measure_number, time_signature=time_signature, events=[])
    
    def _parse_event_line(self, line: str) -> Optional[Event]:
        """Parse event line and return Event object"""
        parts = line.split()
        event_type = parts[0]
        
        # Parse common attributes
        onset = Fraction(parts[1].split('=')[1])
        
        if event_type == "NOTE":
            duration = Fraction(parts[2].split('=')[1])
            pitch_str = parts[3].split('=')[1]
            
            # Parse pitch (e.g., G4, G#4, Gb4)
            pitch_step = pitch_str[0]
            if len(pitch_str) > 2 and pitch_str[1] in ['#', 'b']:
                pitch_alter = 1 if pitch_str[1] == '#' else -1
                octave = int(pitch_str[2:])
            else:
                pitch_alter = 0
                octave = int(pitch_str[1:])
            
            # Parse tie if present
            tie = None
            for part in parts[4:]:
                if part.startswith('tie='):
                    tie = part.split('=')[1]
                    break
            
            return NoteEvent(
                onset=onset,
                duration=duration,
                pitch_step=pitch_step,
                pitch_alter=pitch_alter,
                octave=octave,
                tie=tie if tie != "None" else None
            )
        
        elif event_type == "REST":
            duration = Fraction(parts[2].split('=')[1])
            return RestEvent(onset=onset, duration=duration)
        
        elif event_type == "HARMONY":
            symbol = parts[2].split('=')[1]
            return HarmonyEvent(onset=onset, harmony=symbol)
        
        elif event_type == "LYRIC":
            text = parts[2].split('=')[1]
            return LyricEvent(onset=onset, text=text)
        
        return None