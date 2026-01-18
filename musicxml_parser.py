from music21 import converter, stream, note, harmony
from fractions import Fraction
from typing import Dict, List, Any, Optional, Union
from ikr_light import Score, Part, Voice, Measure, Event, NoteEvent, RestEvent, HarmonyEvent


class MusicXMLParser:
    def __init__(self):
        pass
    
    def parse(self, musicxml_path: str) -> Score:
        """Parse MusicXML file and convert to IKR-light structure"""
        parsed = converter.parse(musicxml_path)
        
        # Handle different return types from music21
        score = None
        if hasattr(parsed, 'scores') and getattr(parsed, 'scores', None):
            score = getattr(parsed, 'scores')[0]  # Opus case
        elif hasattr(parsed, 'parts') and getattr(parsed, 'parts', None):
            score = parsed  # Score case
        else:
            # Create a dummy score if we can't find parts
            score = stream.Score()
            score.append(parsed)
        
        # Extract metadata
        metadata = self._extract_metadata(score)
        
        # Process parts
        parts = []
        if hasattr(score, 'parts') and getattr(score, 'parts', None):
            for part in getattr(score, 'parts'):
                ikr_part = self._process_part(part)
                parts.append(ikr_part)
        
        return Score(metadata=metadata, parts=parts)
    
    def _extract_metadata(self, score) -> Dict[str, Any]:
        """Extract metadata from music21 score"""
        metadata = {}
        
        if hasattr(score, 'metadata') and score.metadata:
            if score.metadata.title:
                metadata['title'] = score.metadata.title
            if score.metadata.composer:
                metadata['composer'] = score.metadata.composer
            if score.metadata.lyricist:
                metadata['lyricist'] = score.metadata.lyricist
        
        return metadata
    
    def _process_part(self, part) -> Part:
        """Process a music21 part and convert to IKR-light Part"""
        part_id = str(part.id) if part.id else str(id(part))
        part_name = getattr(part, 'partName', "") or ""
        
        # Determine role (choir vs instrument)
        role = "instrument"
        if hasattr(part, 'getInstruments'):
            instruments = part.getInstruments()
            if any("choir" in str(instr).lower() or "voice" in str(instr).lower() 
                   for instr in instruments):
                role = "choir"
        
        # Group by voices
        voices_map = self._extract_voices(part)
        
        voices = []
        for voice_id, voice_measures in voices_map.items():
            voice = Voice(id=voice_id, measures=voice_measures)
            voices.append(voice)
        
        return Part(id=part_id, name=part_name, role=role, voices=voices)
    
    def _extract_voices(self, part: stream.Part) -> Dict[str, List[Measure]]:
        """Extract voices and organize by measures"""
        voices_map = {}
        
        # Get measures
        measures = part.getElementsByClass(stream.Measure)
        
        for measure in measures:
            measure_number = measure.number
            time_signature = self._get_time_signature(measure)
            
            # Group events by voice
            voice_events = self._group_events_by_voice(measure)
            
            for voice_id, events in voice_events.items():
                if voice_id not in voices_map:
                    voices_map[voice_id] = []
                
                # Normalize timeline
                normalized_events = self._normalize_timeline(events)
                
                ikr_measure = Measure(
                    number=measure_number,
                    time_signature=time_signature,
                    events=normalized_events
                )
                
                voices_map[voice_id].append(ikr_measure)
        
        return voices_map
    
    def _get_time_signature(self, measure) -> str:
        """Extract time signature from measure"""
        ts = None
        if hasattr(measure, 'timeSignature'):
            ts = measure.timeSignature
        elif hasattr(measure, 'getTimeSignature'):
            ts = measure.getTimeSignature()
        
        if ts:
            return f"{ts.numerator}/{ts.denominator}"
        return "4/4"  # default
    
    def _group_events_by_voice(self, measure: stream.Measure) -> Dict[str, List[Event]]:
        """Group events by voice ID"""
        voice_events = {}
        
        for element in measure.notesAndRests:
            voice_id = getattr(element, 'voice', 1)
            voice_id = str(voice_id)
            
            if voice_id not in voice_events:
                voice_events[voice_id] = []
            
            event = self._convert_element_to_event(element)
            if event:
                voice_events[voice_id].append(event)
        
        # Process harmonies separately
        for element in measure.getElementsByClass(harmony.Harmony):
            voice_id = "1"  # harmonies typically belong to voice 1
            if voice_id not in voice_events:
                voice_events[voice_id] = []
            
            event = self._convert_harmony_to_event(element)
            if event:
                voice_events[voice_id].append(event)
        
        return voice_events
    
    def _convert_element_to_event(self, element) -> Optional[Event]:
        """Convert music21 element to IKR-light Event"""
        onset = Fraction(element.offset)
        duration = Fraction(element.quarterLength)
        
        if isinstance(element, note.Note):
            pitch_alter = 0
            if element.pitch.accidental and element.pitch.accidental.alter is not None:
                pitch_alter = int(element.pitch.accidental.alter)
            
            octave = element.octave if element.octave is not None else 4
            
            tie = None
            if element.tie:
                tie = element.tie.type
            
            return NoteEvent(
                onset=onset,
                duration=duration,
                pitch_step=element.step,
                pitch_alter=pitch_alter,
                octave=octave,
                tie=tie
            )
        elif hasattr(element, 'isRest') and element.isRest:
            return RestEvent(onset=onset, duration=duration)
        
        return None
    
    def _convert_harmony_to_event(self, harmony_element) -> Event:
        """Convert harmony element to IKR-light Event"""
        onset = Fraction(harmony_element.offset)
        
        # Get harmony symbol
        harmony_text = ""
        if harmony_element.figure:
            harmony_text = str(harmony_element.figure)
        
        return HarmonyEvent(onset=onset, harmony=harmony_text)
    
    def _normalize_timeline(self, events: List[Event]) -> List[Event]:
        """Normalize timeline within measure - sort by onset"""
        return sorted(events, key=lambda e: e.onset)