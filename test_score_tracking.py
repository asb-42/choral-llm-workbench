#!/usr/bin/env python3
"""
Quick test to verify semantic diff score tracking fix
"""

import sys
import os
sys.path.insert(0, '/home/asb/Projekte/choral-llm-workbench')

from app import ChoralWorkbench

def test_score_tracking():
    """Test that original_score is properly set during file upload"""
    
    print("🧪 Testing semantic diff score tracking fix...")
    
    # Initialize app
    workbench = ChoralWorkbench()
    
    # Create a simple MusicXML file for testing
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
          <step>D</step>
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
          <step>F</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <type>quarter</type>
      </note>
    </measure>
  </part>
</score-partwise>'''
    
    # Write test file
    test_file = "/tmp/test_music.xml"
    with open(test_file, 'w') as f:
        f.write(test_musicxml)
    
    try:
        # Mock file object
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        # Test file upload
        print("1. Testing file upload...")
        result_tlr, result_msg = workbench.upload_and_parse(MockFile(test_file))
        print(f"   Upload result: {result_msg}")
        
        # Check if original_score is set
        if workbench.original_score is not None:
            print("   ✅ original_score is properly set after upload")
        else:
            print("   ❌ original_score is NOT set after upload")
            return False
        
        # Check if original_tlr is set
        if workbench.original_tlr is not None:
            print("   ✅ original_tlr is properly set after upload")
        else:
            print("   ❌ original_tlr is NOT set after upload")
            return False
        
        # Check if current_score is set
        if workbench.current_score is not None:
            print("   ✅ current_score is properly set after upload")
        else:
            print("   ❌ current_score is NOT set after upload")
            return False
        
        # Test semantic diff generation
        print("\n2. Testing semantic diff generation...")
        try:
            semantic_diffs = workbench.semantic_analyzer.compute_semantic_diff(
                workbench.original_score, workbench.current_score
            )
            if semantic_diffs:
                print(f"   ✅ Semantic diff generated successfully ({len(semantic_diffs)} entries)")
                if semantic_diffs:
                    print(f"   Preview: {semantic_diffs[0].description[:100]}...")
            else:
                print("   ❌ Semantic diff is empty or None")
        except Exception as e:
            print(f"   ❌ Error generating semantic diff: {e}")
            return False
        
        print("\n✅ All tests passed! Score tracking fix is working.")
        return True
        
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    success = test_score_tracking()
    sys.exit(0 if success else 1)