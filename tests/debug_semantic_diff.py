#!/usr/bin/env python3
"""
Debug Semantic Diff Analysis
"""

import sys
import os
sys.path.insert(0, '/home/asb/Projekte/choral-llm-workbench')

from app import ChoralWorkbench
from ikr_light import Score, Part, Voice, Measure, NoteEvent
from fractions import Fraction

def debug_semantic_diff():
    """Debug why semantic diff shows status instead of changes"""
    
    print("🔍 DEBUG: Semantic Diff Analysis")
    print("=" * 50)
    
    # Testdaten
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
    </measure>
  </part>
</score-partwise>'''
    
    test_file = "/tmp/debug_semantic.xml"
    with open(test_file, 'w') as f:
        f.write(test_musicxml)
    
    class MockFile:
        def __init__(self, name):
            self.name = name
    
    workbench = ChoralWorkbench()
    
    try:
        # 1. Upload
        print("1. 📁 Upload & Parse...")
        result_tlr, result_msg = workbench.upload_and_parse(MockFile(test_file))
        print(f"   Result: {result_msg}")
        
        # 2. Transform
        print("\n2. 🔄 Transform...")
        transformed_tlr, transform_msg = workbench.transform_with_validation(
            result_tlr, "Transpose up 2 steps", True, False, False, False
        )
        print(f"   Result: {transform_msg}")
        
        # 3. Debug score states
        print("\n3. 🔍 Debug Score States...")
        print(f"   original_score: {workbench.original_score is not None}")
        print(f"   current_score: {workbench.current_score is not None}")
        print(f"   original_tlr: {workbench.original_tlr is not None}")
        print(f"   _last_transformed_tlr: {hasattr(workbench, '_last_transformed_tlr') and workbench._last_transformed_tlr is not None}")
        
        if workbench.original_score:
            print(f"   original_score parts: {len(workbench.original_score.parts) if workbench.original_score else 'None'}")
        
        if workbench.current_score:
            print(f"   current_score parts: {len(workbench.current_score.parts) if workbench.current_score else 'None'}")
        
        # 4. Test semantic analysis directly
        print("\n4. 🧪 Test Semantic Analysis Directly...")
        if workbench.original_score and workbench.current_score:
            try:
                semantic_diffs = workbench.semantic_analyzer.compute_semantic_diff(
                    workbench.original_score, workbench.current_score
                )
                print(f"   Raw semantic diffs: {len(semantic_diffs)} entries")
                for i, diff in enumerate(semantic_diffs[:3]):
                    print(f"     {i+1}. {diff.change_type}: {diff.description}")
                
                if semantic_diffs:
                    html_output = workbench.semantic_ui.render_semantic_diff_html(semantic_diffs)
                    print(f"   HTML preview: {html_output[:200]}...")
                else:
                    print("   ⚠️ No semantic diffs generated")
            except Exception as e:
                print(f"   ❌ Semantic analysis error: {e}")
        else:
            print("   ❌ Cannot analyze: missing original_score or current_score")
        
        # 5. Test update_semantic_diff_display()
        print("\n5. 🖥️ Test update_semantic_diff_display()...")
        final_output = workbench.update_semantic_diff_display()
        print(f"   Final output length: {len(final_output)} chars")
        print(f"   Final output preview: {final_output[:300]}...")
        
        # Check if it's the fallback
        if "✅ Transformation completed successfully" in final_output:
            print("   ❌ Using fallback status instead of actual semantic diff!")
            return False
        elif "📝 System Changes" in final_output:
            print("   ✅ Using actual semantic diff!")
            return True
        else:
            print("   ❓ Unknown output format")
            return False
    
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    success = debug_semantic_diff()
    sys.exit(0 if success else 1)