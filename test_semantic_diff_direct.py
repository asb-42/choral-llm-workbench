#!/usr/bin/env python3
"""
Quick test to verify semantic diff works with simple manual input
"""

import sys
import os
sys.path.insert(0, '/home/asb/Projekte/choral-llm-workbench')

from app import ChoralWorkbench
from ikr_light import Score, Part, Voice, Measure, NoteEvent
from fractions import Fraction

def test_semantic_diff_directly():
    """Test semantic diff with manually created scores"""
    
    print("🧪 Testing semantic diff directly...")
    
    # Initialize app
    workbench = ChoralWorkbench()
    
    # Create original score manually
    original_score = Score(metadata={}, parts=[])
    
    # Add part
    part = Part(id="P1", name="Piano", role="instrument", voices=[])
    original_score.parts.append(part)
    
    # Add voice
    voice = Voice(id="V1", measures=[])
    part.voices.append(voice)
    
    # Add measure
    measure = Measure(number=1, time_signature="4/4", events=[])
    voice.measures.append(measure)
    
    # Add notes C4, D4, E4, F4
    measure.events.append(NoteEvent(onset=Fraction(0, 1), duration=Fraction(1, 1), pitch_step="C", pitch_alter=0, octave=4))
    measure.events.append(NoteEvent(onset=Fraction(1, 1), duration=Fraction(1, 1), pitch_step="D", pitch_alter=0, octave=4))
    measure.events.append(NoteEvent(onset=Fraction(2, 1), duration=Fraction(1, 1), pitch_step="E", pitch_alter=0, octave=4))
    measure.events.append(NoteEvent(onset=Fraction(3, 1), duration=Fraction(1, 1), pitch_step="F", pitch_alter=0, octave=4))
    
    # Create transformed score (transposed up)
    transformed_score = Score(metadata={}, parts=[])
    
    # Add part
    part2 = Part(id="P1", name="Piano", role="instrument", voices=[])
    transformed_score.parts.append(part2)
    
    # Add voice
    voice2 = Voice(id="V1", measures=[])
    part2.voices.append(voice2)
    
    # Add measure
    measure2 = Measure(number=1, time_signature="4/4", events=[])
    voice2.measures.append(measure2)
    
    # Add notes D4, E4, F#4, G4 (transposed up by major 2nd)
    measure2.events.append(NoteEvent(onset=Fraction(0, 1), duration=Fraction(1, 1), pitch_step="D", pitch_alter=0, octave=4))
    measure2.events.append(NoteEvent(onset=Fraction(1, 1), duration=Fraction(1, 1), pitch_step="E", pitch_alter=0, octave=4))
    measure2.events.append(NoteEvent(onset=Fraction(2, 1), duration=Fraction(1, 1), pitch_step="F", pitch_alter=1, octave=4))  # F#
    measure2.events.append(NoteEvent(onset=Fraction(3, 1), duration=Fraction(1, 1), pitch_step="G", pitch_alter=0, octave=4))
    
    print("1. Original score created with notes: C4, D4, E4, F4")
    print("2. Transformed score created with notes: D4, E4, F#4, G4")
    
    # Test semantic diff
    print("\n3. 🔄 Testing semantic diff generation...")
    try:
        semantic_diffs = workbench.semantic_analyzer.compute_semantic_diff(
            original_score, transformed_score
        )
        
        if semantic_diffs:
            print(f"   ✅ Semantic diff generated successfully ({len(semantic_diffs)} entries):")
            for i, diff in enumerate(semantic_diffs):
                print(f"     {i+1}. [{diff.scope}] {diff.change_type}: {diff.description}")
                if diff.before_value and diff.after_value:
                    print(f"        Before: {diff.before_value} → After: {diff.after_value}")
        else:
            print("   ❌ No semantic differences found")
            return False
            
    except Exception as e:
        print(f"   ❌ Semantic diff error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test UI rendering
    print("\n4. 🖥️ Testing UI rendering...")
    try:
        html_output = workbench.semantic_ui.render_semantic_diff_html(semantic_diffs)
        if html_output and len(html_output.strip()) > 10:
            print("   ✅ HTML rendering successful")
            print(f"   Preview: {html_output[:150]}...")
        else:
            print("   ❌ HTML rendering failed")
            return False
    except Exception as e:
        print(f"   ❌ HTML rendering error: {e}")
        return False
    
    print("\n✅ Semantic diff direct test successful!")
    return True

if __name__ == "__main__":
    success = test_semantic_diff_directly()
    sys.exit(0 if success else 1)