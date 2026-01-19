#!/usr/bin/env python3
"""
Test the improved musical language and transposition grouping
"""

import sys
import os
sys.path.insert(0, '/home/asb/Projekte/choral-llm-workbench')

from app import ChoralWorkbench

def test_musical_language_improvements():
    """Test the new musical language features"""
    
    print("🎵 TESTING MUSICAL LANGUAGE IMPROVEMENTS")
    print("=" * 50)
    
    # Test 1: Duration to note names
    print("\n1. 🎼 Testing Duration-to-Note Names:")
    analyzer = ChoralWorkbench().semantic_analyzer
    
    from fractions import Fraction
    
    test_cases = [
        Fraction(1, 4),  # quarter note
        Fraction(1, 2),  # half note  
        Fraction(1, 8),  # eighth note
        Fraction(3, 8),  # dotted quarter note
    ]
    
    for duration in test_cases:
        note_name = analyzer._duration_to_note_name(duration)
        print(f"   {duration} → {note_name}")
    
    # Test 2: Pitch change with intervals
    print("\n2. 🎹 Testing Pitch Change Analysis:")
    from ikr_light import NoteEvent
    from fractions import Fraction
    from semantic_diff_analyzer import SemanticDiffEntry
    
    before_note = NoteEvent(onset=Fraction(0, 1), duration=Fraction(1, 4), pitch_step="C", pitch_alter=0, octave=4, tie=None)
    after_note = NoteEvent(onset=Fraction(0, 1), duration=Fraction(1, 4), pitch_step="D", pitch_alter=0, octave=5, tie=None)
    
    pitch_analysis = analyzer._analyze_pitch_change_with_interval(before_note, after_note)
    print(f"   C4 → D5:")
    print(f"   Direction: {pitch_analysis['direction']}")
    print(f"   Semitones: {pitch_analysis['absolute_semitones']}")
    print(f"   Interval: {pitch_analysis['interval_type']}")
    
    # Test 3: Transposition detection
    print("\n3. 🔄 Testing Transposition Detection:")
    # Simulate a transposition (C major → D major) - these should be detected as +2 semitones
    transposition_notes = [
        SemanticDiffEntry("note", "test", "pitch", "Pitch changed: C4 → D4 (+2 semitones)"),
        SemanticDiffEntry("note", "test", "pitch", "Pitch changed: E4 → F#4 (+2 semitones)"),
        SemanticDiffEntry("note", "test", "pitch", "Pitch changed: G4 → A4 (+2 semitones)")
    ]
    
    # Convert to SemanticDiffEntry objects
    from semantic_diff_analyzer import SemanticDiffEntry
    pitch_changes = [
        SemanticDiffEntry(scope="note", location="test", change_type="pitch", description="Pitch changed: C4 → D4 (+2 semitones)"),
        SemanticDiffEntry(scope="note", location="test", change_type="pitch", description="Pitch changed: E4 → F#4 (+2 semitones)"),
        SemanticDiffEntry(scope="note", location="test", change_type="pitch", description="Pitch changed: G4 → A4 (+2 semitones)")
    ]
    
    transposition_info = analyzer._detect_transposition(pitch_changes)
    if transposition_info and transposition_info['is_transposition']:
        print(f"   ✅ Transposition detected:")
        print(f"   Direction: {transposition_info['direction']}")
        print(f"   Interval: {transposition_info['interval_name']}")
        print(f"   Semitones: {transposition_info['absolute_semitones']}")
        print(f"   Note count: {transposition_info['note_count']}")
    else:
        print("   ❌ No transposition detected")
    
    # Test 4: Complete transformation with MusicXML
    print("\n4. 🎯 Testing Complete Pipeline:")
    test_musicxml = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1">
      <part-name>Piano</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
        <key>
          <fifths>0</fifths>
        </key>
        <time>
          <beats>4</beats>
          <beat-type>4</beat-type>
        </time>
        <clef>
          <sign>G</sign>
          <line>2</line>
        </clef>
      </attributes>
      <note>
        <pitch>
          <step>C</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <type>quarter</type>
      </note>
      <note>
        <pitch>
          <step>G</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <type>quarter</type>
      </note>
    </measure>
  </part>
</score-partwise>'''
    
    test_file = "/tmp/test_musical_language.xml"
    with open(test_file, 'w') as f:
        f.write(test_musicxml)
    
    class MockFile:
        def __init__(self, name):
            self.name = name
    
    workbench = ChoralWorkbench()
    
    try:
        # Upload original
        result_tlr, _ = workbench.upload_and_parse(MockFile(test_file))
        print(f"   Upload: ✅")
        
        # Transform (transpose up 2 semitones)
        transformed_tlr, transform_msg = workbench.transform_with_validation(
            result_tlr, "Transpose up by major second", True, False, False, False
        )
        print(f"   Transform: {transform_msg}")
        
        # Generate semantic diff
        if workbench.original_score and workbench.current_score:
            semantic_diffs = workbench.semantic_analyzer.compute_semantic_diff(
                workbench.original_score, workbench.current_score
            )
        else:
            semantic_diffs = []
        
        print(f"   Semantic diff entries: {len(semantic_diffs)}")
        for i, diff in enumerate(semantic_diffs[:5], 1):
            print(f"     {i}. [{diff.change_type}] {diff.description}")
        
        if semantic_diffs:
            # Render HTML
            html_output = workbench.semantic_ui.render_semantic_diff_html(semantic_diffs)
            print(f"   HTML output length: {len(html_output)} characters")
            
            # Check for improved musical language
            if "quarter note" in html_output:
                print("   ✅ Musical duration names detected")
            if "semitones" in html_output:
                print("   ✅ Interval information detected")
            if "Transposed up" in html_output:
                print("   ✅ Transposition grouping detected")
            else:
                print("   ⚠️ Transposition grouping not detected")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test_musical_language_improvements()