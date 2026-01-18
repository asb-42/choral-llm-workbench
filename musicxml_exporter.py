from music21 import stream, note, harmony, metadata, instrument
from fractions import Fraction
from typing import Dict, List, Optional, Any
from ikr_light import Score, Part, Voice, Measure, Event, NoteEvent, RestEvent, HarmonyEvent, LyricEvent


class MusicXMLExporter:
    """Export IKR-light Score to MusicXML using music21"""
    
    def __init__(self):
        pass
    
    def export(self, score: Score, output_path: str) -> bool:
        """Export IKR-light Score to MusicXML file"""
        try:
            # Create music21 score
            m21_score = stream.Score()
            
            # Add metadata
            self._add_metadata(m21_score, score.metadata)
            
            # Process parts
            for part in score.parts:
                m21_part = self._create_part(part)
                m21_score.append(m21_part)
            
            # Write to MusicXML
            m21_score.write("musicxml", fp=output_path)
            return True
            
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    def _add_metadata(self, m21_score: stream.Score, ikr_metadata: Dict):
        """Add metadata to music21 score"""
        if not ikr_metadata:
            return
        
        m21_metadata = metadata.Metadata()
        
        if 'title' in ikr_metadata:
            m21_metadata.title = ikr_metadata['title']
        if 'composer' in ikr_metadata:
            m21_metadata.composer = ikr_metadata['composer']
        if 'lyricist' in ikr_metadata:
            m21_metadata.lyricist = ikr_metadata['lyricist']
        
        m21_score.insert(0, m21_metadata)
    
    def _create_part(self, ikr_part: Part) -> stream.Part:
        """Create music21 Part from IKR-light Part"""
        m21_part = stream.Part()
        m21_part.id = ikr_part.id
        m21_part.partName = ikr_part.name
        
        # Add instrument based on role
        if ikr_part.role == "choir":
            # Use appropriate choir instrument
            instr = instrument.Soprano()
            m21_part.insert(0, instr)
        else:
            # Use generic instrument
            instr = instrument.Instrument()
            m21_part.insert(0, instr)
        
        # Process voices
        for voice in ikr_part.voices:
            self._add_voice_to_part(m21_part, voice)
        
        return m21_part
    
    def _add_voice_to_part(self, m21_part: stream.Part, voice: Voice):
        """Add voice events to part"""
        # Group events by measure
        measures_dict = {}
        for measure in voice.measures:
            measures_dict[measure.number] = measure
        
        # Create measures in order
        if measures_dict:
            for measure_num in sorted(measures_dict.keys()):
                measure = measures_dict[measure_num]
                m21_measure = self._create_measure(measure, voice.id)
                m21_part.append(m21_measure)
    
    def _create_measure(self, ikr_measure: Measure, voice_id: str) -> stream.Measure:
        """Create music21 Measure from IKR-light Measure"""
        m21_measure = stream.Measure()
        m21_measure.number = ikr_measure.number
        
        # Add time signature
        self._add_time_signature(m21_measure, ikr_measure.time_signature)
        
        # Sort events by onset
        sorted_events = sorted(ikr_measure.events, key=lambda e: e.onset)
        
        # Add events to measure
        for event in sorted_events:
            m21_element = self._create_m21_element(event, voice_id)
            if m21_element:
                m21_measure.insert(float(event.onset), m21_element)
        
        return m21_measure
    
    def _add_time_signature(self, m21_measure: stream.Measure, time_signature: str):
        """Add time signature to measure"""
        try:
            from music21 import meter
            parts = time_signature.split('/')
            numerator = int(parts[0])
            denominator = int(parts[1])
            
            ts = meter.TimeSignature(str(numerator) + '/' + str(denominator))
            m21_measure.insert(0, ts)
        except (ValueError, IndexError):
            # Default to 4/4 if invalid
            from music21 import meter
            ts = meter.TimeSignature("4/4")
            m21_measure.insert(0, ts)
    
    def _create_m21_element(self, event: Event, voice_id: str):
        """Create music21 element from IKR-light Event"""
        if isinstance(event, NoteEvent):
            return self._create_note(event, voice_id)
        elif isinstance(event, RestEvent):
            return self._create_rest(event, voice_id)
        elif isinstance(event, HarmonyEvent):
            return self._create_harmony(event)
        elif isinstance(event, LyricEvent):
            # Lyrics are attached to notes, not standalone
            return None
        
        return None
    
    def _create_note(self, note_event: NoteEvent, voice_id: str) -> note.Note:
        """Create music21 Note from NoteEvent"""
        # Create pitch
        pitch_str = f"{note_event.pitch_step}{note_event.octave}"
        if note_event.pitch_alter == 1:
            pitch_str += "#"
        elif note_event.pitch_alter == -1:
            pitch_str += "-"
        elif note_event.pitch_alter == 2:
            pitch_str += "##"
        elif note_event.pitch_alter == -2:
            pitch_str += "--"
        
        m21_note = note.Note(pitch_str)
        
        # Set duration
        m21_note.quarterLength = float(note_event.duration)
        
        # Set voice (stored as lyric for now, since voice attribute doesn't exist)
        # m21_note.voice = voice_id
        
        # Set tie if present
        if note_event.tie:
            from music21 import tie
            if note_event.tie == "start":
                m21_note.tie = tie.Tie("start")
            elif note_event.tie == "stop":
                m21_note.tie = tie.Tie("stop")
        
        return m21_note
    
    def _create_rest(self, rest_event: RestEvent, voice_id: str) -> note.Rest:
        """Create music21 Rest from RestEvent"""
        m21_rest = note.Rest()
        m21_rest.quarterLength = float(rest_event.duration)
        # Set voice (stored as lyric for now, since voice attribute doesn't exist)
        # m21_rest.voice = voice_id
        return m21_rest
    
    def _create_harmony(self, harmony_event: HarmonyEvent) -> harmony.Harmony:
        """Create music21 Harmony from HarmonyEvent"""
        m21_harmony = harmony.Harmony()
        
        # Set harmony symbol
        if harmony_event.harmony:
            m21_harmony.figure = harmony_event.harmony
        
        # Set key as lyric/comment for now (music21 Harmony doesn't have key field)
        if harmony_event.key:
            # Store key information in harmony figure with special format
            if m21_harmony.figure:
                m21_harmony.figure = f"{m21_harmony.figure} (key: {harmony_event.key})"
            else:
                m21_harmony.figure = f"key: {harmony_event.key}"
        
        # Set offset (onset)
        m21_harmony.offset = float(harmony_event.onset)
        
        return m21_harmony