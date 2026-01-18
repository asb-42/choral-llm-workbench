from typing import Dict, List, Optional, Tuple
from ikr_light import Score, Part, Voice, Measure, Event
from fractions import Fraction


class EventIndexer:
    """Create unique IDs for events and enable reference-based access"""
    
    def __init__(self):
        self.event_to_id = {}
        self.id_to_event = {}
        self.next_id = 1
    
    def index_score(self, score: Score) -> Dict[str, any]:
        """Index all events in score and return lookup structure"""
        self.event_to_id = {}
        self.id_to_event = {}
        self.next_id = 1
        
        index_structure = {
            'parts': {},
            'events_by_part': {},
            'events_by_voice': {},
            'events_by_measure': {},
            'event_hierarchy': {}
        }
        
        for part in score.parts:
            part_id = f"part_{part.id}"
            index_structure['parts'][part_id] = {
                'name': part.name,
                'role': part.role,
                'voices': {}
            }
            index_structure['events_by_part'][part_id] = {}
            
            for voice in part.voices:
                voice_id = f"voice_{voice.id}"
                index_structure['parts'][part_id]['voices'][voice_id] = {
                    'voice_id': voice.id,
                    'measures': {}
                }
                index_structure['events_by_voice'][voice_id] = {}
                
                for measure in voice.measures:
                    measure_id = f"measure_{measure.number}"
                    index_structure['parts'][part_id]['voices'][voice_id]['measures'][measure_id] = {
                        'number': measure.number,
                        'time_signature': measure.time_signature,
                        'events': []
                    }
                    index_structure['events_by_measure'][measure_id] = {}
                    
                    # Sort events by onset for consistent indexing
                    sorted_events = sorted(measure.events, key=lambda e: e.onset)
                    
                    for event in sorted_events:
                        event_id = f"event_{self.next_id}"
                        self.next_id += 1
                        
                        # Store mappings - use event string representation as key since objects aren't hashable
                        event_key = str(event)
                        self.event_to_id[event_key] = event_id
                        self.id_to_event[event_id] = event
                        
                        # Add to index structure
                        index_structure['parts'][part_id]['voices'][voice_id]['measures'][measure_id]['events'].append(event_id)
                        index_structure['events_by_part'][part_id][event_id] = {
                            'event': event,
                            'voice_id': voice_id,
                            'measure_id': measure_id,
                            'part_id': part_id
                        }
                        index_structure['events_by_voice'][voice_id][event_id] = {
                            'event': event,
                            'measure_id': measure_id,
                            'part_id': part_id
                        }
                        index_structure['events_by_measure'][measure_id][event_id] = {
                            'event': event,
                            'voice_id': voice_id,
                            'part_id': part_id
                        }
                        
                        # Hierarchy information
                        index_structure['event_hierarchy'][event_id] = {
                            'part': part_id,
                            'voice': voice_id,
                            'measure': measure_id,
                            'event_type': type(event).__name__
                        }
        
        return index_structure
    
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get event by its unique ID"""
        return self.id_to_event.get(event_id)
    
    def get_event_id(self, event: Event) -> Optional[str]:
        """Get ID for an event"""
        return self.event_to_id.get(event)
    
    def format_event_reference(self, event_id: str) -> str:
        """Format event reference for user display"""
        if event_id not in self.id_to_event:
            return f"Unknown event: {event_id}"
        
        hierarchy = self._find_hierarchy_for_event(event_id)
        if not hierarchy:
            return event_id
        
        return f"{hierarchy['part_name']} - Voice {hierarchy['voice_id']} - Measure {hierarchy['measure_number']} - Event {event_id}"
    
    def _find_hierarchy_for_event(self, event_id: str) -> Optional[Dict]:
        """Find hierarchical information for event"""
        # This would be populated during indexing
        # For now, return basic info
        return {
            'part_name': 'Unknown',
            'voice_id': 'Unknown',
            'measure_number': 'Unknown'
        }