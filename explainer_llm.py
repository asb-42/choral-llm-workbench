from typing import Dict, List, Optional, Tuple
from ollama_llm import OllamaLLM
from tlr_converter import TLRConverter
from event_indexer import EventIndexer
from ikr_light import Score


class ExplainerLLM:
    """Separate LLM interface for explanation mode (read-only)"""
    
    def __init__(self, model_name: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.llm = OllamaLLM(model_name, base_url)
        self.tlr_converter = TLRConverter()
        self.event_indexer = EventIndexer()
        
        # Explanation-specific system prompt
        self.system_prompt = """You are analyzing musical transformations and explaining musical decisions.
Rules:
- You can only read and analyze, never modify the music.
- Reference events using their unique IDs (event_1, event_2, etc.).
- Always include part name, voice number, and measure number in your explanations.
- Explain musical reasoning behind transformations.
- If you don't know why something was changed, say so explicitly.
- Be specific about harmonic, melodic, and rhythmic relationships.

Available reference format:
- Part: "Soprano", "Alto", "Tenor", "Bass" etc.
- Voice: voice_1, voice_2, etc.
- Measure: measure_1, measure_2, etc.
- Event: event_1, event_2, etc.

Example response structure:
"The F# in Alto voice (event_12) in measure 8 was lowered to F (event_45) because..."

If you cannot identify a specific event, ask for clarification about the event ID or location."""
    
    def explain_transformation(self, original_score: Score, transformed_score: Score, question: str) -> Tuple[str, List[str]]:
        """Explain transformation between original and transformed scores"""
        
        # Index both scores for event reference
        original_index = self.event_indexer.index_score(original_score)
        transformed_index = self.event_indexer.index_score(transformed_score)
        
        # Convert both to TLR for analysis
        original_tlr = self.tlr_converter.ikr_to_tlr(original_score)
        transformed_tlr = self.tlr_converter.ikr_to_tlr(transformed_score)
        
        # Build analysis prompt
        analysis_prompt = f"""Analyze this musical transformation and answer the user's question.

ORIGINAL MUSIC:
{original_tlr}

TRANSFORMED MUSIC:
{transformed_tlr}

EVENT INDEXING:
Original events: {list(original_index['event_hierarchy'].keys())[:10]}... (showing first 10)
Transformed events: {list(transformed_index['event_hierarchy'].keys())[:10]}... (showing first 10)

PART STRUCTURE:
Original parts: {list(original_index['parts'].keys())}
Transformed parts: {list(transformed_index['parts'].keys())}

USER QUESTION:
{question}

Please explain what happened by referencing specific event IDs and their locations."""
        
        try:
            # Get explanation from LLM
            response = self.llm._call_ollama(self.system_prompt, analysis_prompt)
            return response.strip(), []
            
        except Exception as e:
            return f"Error getting explanation: {str(e)}", [str(e)]
    
    def explain_score_context(self, score: Score, question: str) -> Tuple[str, List[str]]:
        """Explain context within a single score"""
        
        # Index the score
        index = self.event_indexer.index_score(score)
        
        # Convert to TLR
        tlr_text = self.tlr_converter.ikr_to_tlr(score)
        
        # Build context prompt
        context_prompt = f"""Analyze this musical score and answer the user's question.

MUSIC:
{tlr_text}

EVENT INDEXING:
Events: {list(index['event_hierarchy'].keys())[:10]}... (showing first 10)

PART STRUCTURE:
Parts: {list(index['parts'].keys())}

MEASURES:
{', '.join([f"measure_{i}" for i in range(1, 6)])}... (showing first 5)

USER QUESTION:
{question}

Please analyze the music and answer using specific event IDs and locations."""
        
        try:
            # Get explanation from LLM
            response = self.llm._call_ollama(self.system_prompt, context_prompt)
            return response.strip(), []
            
        except Exception as e:
            return f"Error getting explanation: {str(e)}", [str(e)]
    
    def get_event_summary(self, score: Score) -> str:
        """Get summary of all events with their IDs"""
        
        index = self.event_indexer.index_score(score)
        
        summary_parts = []
        summary_parts.append("EVENT SUMMARY:")
        summary_parts.append("=" * 50)
        
        for part_id, part_info in index['parts'].items():
            part_name = part_info['name']
            summary_parts.append(f"\nPART: {part_name} ({part_id})")
            
            for voice_id, voice_info in part_info['voices'].items():
                voice_num = voice_id.replace('voice_', '')
                summary_parts.append(f"  VOICE {voice_num}:")
                
                for measure_id, measure_info in voice_info['measures'].items():
                    measure_num = measure_id.replace('measure_', '')
                    time_sig = measure_info['time_signature']
                    summary_parts.append(f"    MEASURE {measure_num} ({time_sig}):")
                    
                    for event_id in measure_info['events']:
                        # Get event details
                        event_info = index['event_hierarchy'][event_id]
                        event_type = event_info['event_type']
                        summary_parts.append(f"      {event_id}: {event_type}")
        
        return "\n".join(summary_parts)