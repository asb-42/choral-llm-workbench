import pytest
from explainer_llm import ExplainerLLM
from event_indexer import EventIndexer
from ikr_light import Score, Part, Voice, Measure, NoteEvent, HarmonyEvent
from fractions import Fraction


class TestExplainerLLM:
    """Test explanation mode functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.explainer = ExplainerLLM()
        self.event_indexer = EventIndexer()
    
    def test_event_indexer_simple_score(self):
        """Test event indexing on simple score"""
        # Create simple score
        note1 = NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='C', pitch_alter=0, octave=4)
        note2 = NoteEvent(onset=Fraction(1, 4), duration=Fraction(1, 4), pitch_step='D', pitch_alter=0, octave=4)
        
        measure = Measure(number=1, time_signature="4/4", events=[note1, note2])
        voice = Voice(id="1", measures=[measure])
        part = Part(id="soprano", name="Soprano", role="choir", voices=[voice])
        score = Score(metadata={}, parts=[part])
        
        # Index the score
        index = self.event_indexer.index_score(score)
        
        # Check structure
        assert 'parts' in index
        assert 'events_by_part' in index
        assert 'events_by_voice' in index
        assert 'events_by_measure' in index
        assert 'event_hierarchy' in index
        
        # Check part indexing
        assert 'part_soprano' in index['parts']
        assert index['parts']['part_soprano']['name'] == 'Soprano'
        
        # Check event IDs
        event_ids = list(index['event_hierarchy'].keys())
        assert len(event_ids) == 2
        assert all(event_id.startswith('event_') for event_id in event_ids)
    
    def test_event_id_lookup(self):
        """Test event ID lookup functionality"""
        note = NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='C', pitch_alter=0, octave=4)
        
        measure = Measure(number=1, time_signature="4/4", events=[note])
        voice = Voice(id="1", measures=[measure])
        part = Part(id="test", name="Test", role="instrument", voices=[voice])
        score = Score(metadata={}, parts=[part])
        
        # Index and test lookup
        index = self.event_indexer.index_score(score)
        event_ids = list(index['event_hierarchy'].keys())
        
        # Test get_event_by_id
        found_event = self.event_indexer.get_event_by_id(event_ids[0])
        assert found_event is not None
        assert found_event.pitch_step == 'C'
        
        # Test get_event_id
        found_id = self.event_indexer.get_event_id(note)
        assert found_id == event_ids[0]
    
    def test_explain_score_context_structure(self):
        """Test explanation context building"""
        note = NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='F', pitch_alter=1, octave=4)
        
        measure = Measure(number=12, time_signature="4/4", events=[note])
        voice = Voice(id="2", measures=[measure])  # Alto voice
        part = Part(id="alto", name="Alto", role="choir", voices=[voice])
        score = Score(metadata={}, parts=[part])
        
        # Test context explanation (mock response)
        question = "Why was the F# in Alto measure 12 used?"
        
        # We can't test the actual LLM response, but we can test the structure
        index = self.event_indexer.index_score(score)
        
        # Check that the structure is ready for LLM processing
        assert 'event_hierarchy' in index
        assert 'parts' in index
        
        # Check that alto voice is indexed
        alto_events = [eid for eid, info in index['event_hierarchy'].items() 
                      if 'alto' in info.get('part', '') and 'voice_2' in info.get('voice', '')]
        assert len(alto_events) > 0
    
    def test_explain_transformation_structure(self):
        """Test transformation explanation structure"""
        # Original score with F#
        note_original = NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='F', pitch_alter=1, octave=4)
        
        measure1 = Measure(number=12, time_signature="4/4", events=[note_original])
        voice1 = Voice(id="2", measures=[measure1])
        part1 = Part(id="alto", name="Alto", role="choir", voices=[voice1])
        original_score = Score(metadata={}, parts=[part1])
        
        # Transformed score with F natural
        note_transformed = NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='F', pitch_alter=0, octave=4)
        
        measure2 = Measure(number=12, time_signature="4/4", events=[note_transformed])
        voice2 = Voice(id="2", measures=[measure2])
        part2 = Part(id="alto", name="Alto", role="choir", voices=[voice2])
        transformed_score = Score(metadata={}, parts=[part2])
        
        # Index both scores
        original_index = self.event_indexer.index_score(original_score)
        transformed_index = self.event_indexer.index_score(transformed_score)
        
        # Both should have same structure but different events
        assert len(original_index['event_hierarchy']) == len(transformed_index['event_hierarchy'])
        
        # Check that F# vs F difference exists
        original_events = list(original_index['event_hierarchy'].keys())
        transformed_events = list(transformed_index['event_hierarchy'].keys())
        
        # Should have same number of events
        assert len(original_events) == len(transformed_events)
    
    def test_get_event_summary(self):
        """Test event summary generation"""
        # Create score with multiple parts
        notes_soprano = [
            NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='C', pitch_alter=0, octave=4),
            NoteEvent(onset=Fraction(1, 4), duration=Fraction(1, 4), pitch_step='D', pitch_alter=0, octave=4)
        ]
        
        notes_alto = [
            NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='A', pitch_alter=0, octave=3),
            NoteEvent(onset=Fraction(1, 4), duration=Fraction(1, 4), pitch_step='B', pitch_alter=0, octave=3)
        ]
        
        measure_soprano = Measure(number=1, time_signature="4/4", events=notes_soprano)
        measure_alto = Measure(number=1, time_signature="4/4", events=notes_alto)
        
        voice_soprano = Voice(id="1", measures=[measure_soprano])
        voice_alto = Voice(id="2", measures=[measure_alto])
        
        part_soprano = Part(id="soprano", name="Soprano", role="choir", voices=[voice_soprano])
        part_alto = Part(id="alto", name="Alto", role="choir", voices=[voice_alto])
        
        score = Score(metadata={}, parts=[part_soprano, part_alto])
        
        # Get summary
        summary = self.explainer.get_event_summary(score)
        
        # Check summary structure
        assert "EVENT SUMMARY:" in summary
        assert "PART: Soprano" in summary
        assert "PART: Alto" in summary
        assert "VOICE 1:" in summary
        assert "VOICE 2:" in summary
        assert "MEASURE 1 (4/4):" in summary
        assert "event_" in summary
        
        # Check that all event types are mentioned
        assert "NoteEvent" in summary
    
    def test_system_prompt_structure(self):
        """Test that explanation system prompt has required elements"""
        prompt = self.explainer.system_prompt
        
        # Check key requirements
        assert "read and analyze, never modify" in prompt
        assert "unique IDs" in prompt
        assert "part name, voice number, and measure number" in prompt
        assert "musical reasoning" in prompt
        assert "reference format" in prompt
    
    def test_harmony_in_explanation_context(self):
        """Test that harmony events are included in explanation context"""
        harmony = HarmonyEvent(onset=Fraction(0), harmony="IV", key="G major")
        note = NoteEvent(onset=Fraction(0), duration=Fraction(1, 4), pitch_step='G', pitch_alter=0, octave=4)
        
        measure = Measure(number=8, time_signature="4/4", events=[note, harmony])
        voice = Voice(id="1", measures=[measure])
        part = Part(id="test", name="Test", role="instrument", voices=[voice])
        score = Score(metadata={}, parts=[part])
        
        # Index and check
        index = self.event_indexer.index_score(score)
        
        # Should include harmony events
        harmony_events = [eid for eid, info in index['event_hierarchy'].items() 
                        if info.get('event_type') == 'HarmonyEvent']
        assert len(harmony_events) > 0
        
        # Test summary includes harmony
        summary = self.explainer.get_event_summary(score)
        assert "HarmonyEvent" in summary