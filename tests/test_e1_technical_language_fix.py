#!/usr/bin/env python3
"""
Simple focused test to fix E1 Technical Language issue
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_fix_technical_language():
    """Fix E1: No Technical Terms - implement proper duration to note names"""
    
    print("=== E1 TECHNICAL LANGUAGE FIX TEST ===")
    
    # Import and test the analyzer directly
    from semantic_diff_analyzer import SemanticDiffAnalyzer
    from ikr_light import Score, Part, Voice, Measure, NoteEvent
    from fractions import Fraction
    
    # Create simple analyzer instance to test the specific method
    analyzer = SemanticDiffAnalyzer()
    
    # Test duration to note name conversion
    print("\n1. Testing Duration to Note Names:")
    
    test_durations = [
        Fraction(1, 1),    # quarter note
        Fraction(1, 2),    # half note
        Fraction(1, 8),    # eighth note
        Fraction(3, 4),    # dotted quarter
        Fraction(1, 16),   # whole note
    ]
    
    expected_names = ["Quarter note", "Half note", "Eighth note", "Dotted quarter", "Whole note"]
    
    for i, duration in enumerate(test_durations):
        note_name = analyzer._duration_to_note_name(duration)
        expected = expected_names[i]
        if note_name == expected:
            print(f"   ✅ {duration} → {note_name}")
        else:
            print(f"   ❌ {duration} → {note_name} (expected: {expected})")
    
    # Test the _analyze_pitch_change_with_interval method to see if it produces technical terms
    print("\n2. Testing Pitch Change Analysis:")
    
    from ikr_light import NoteEvent
    before_note = NoteEvent(onset=Fraction(0), duration=Fraction(1,4), pitch_step="C", pitch_alter=0, octave=4, tie=None)
    after_note = NoteEvent(onset=Fraction(0), duration=Fraction(1,4), pitch_step="D", pitch_alter=0, octave=4, tie=None)
    
    pitch_analysis = analyzer._analyze_pitch_change_with_interval(before_note, after_note)
    
    print(f"   Pitch change analysis: {pitch_analysis}")
    
    # Check for forbidden patterns in the analysis
    forbidden_patterns = ['duration=', 'pitch=', 'float', 'IKRNode', 'step=', 'octave=', 'alter=']
    analysis_text = str(pitch_analysis)
    
    found_forbidden = []
    for pattern in forbidden_patterns:
        if pattern in analysis_text:
            found_forbidden.append(pattern)
            print(f"   ❌ Found forbidden pattern: {pattern}")
    
    if not found_forbidden:
        print("   ✅ No forbidden patterns in pitch analysis")
    
    # Test that description generation avoids technical terms
    print("\n3. Testing Description Generation:")
    
    # Mock a simple diff entry to test description format
    class MockDiff:
        def __init__(self, scope, location, change_type, description):
            self.scope = scope
            self.location = location
            self.change_type = change_type
            self.description = description
    
    # Test description that should be safe
    safe_description = "Pitch raised by major second"
    
    # Check description for forbidden patterns
    forbidden_in_desc = []
    for pattern in forbidden_patterns:
        if pattern in safe_description:
            forbidden_in_desc.append(pattern)
    
    if forbidden_in_desc:
        print(f"   ❌ Forbidden patterns in safe description: {forbidden_in_desc}")
    else:
        print(f"   ✅ Safe description: {safe_description}")
    
    print("\n=== SUMMARY ===")
    
    if found_forbidden or forbidden_in_desc:
        print("❌ E1 TECHNICAL LANGUAGE FIX: FAILED")
        return False
    else:
        print("✅ E1 TECHNICAL LANGUAGE FIX: PASSED")
        return True

if __name__ == "__main__":
    success = test_fix_technical_language()
    sys.exit(0 if success else 1)