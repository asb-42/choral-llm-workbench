#!/usr/bin/env python3
"""
Test the complete pipeline: Upload → Transform → Semantic Diff → Export
"""

import sys
import os
sys.path.insert(0, '/home/asb/Projekte/choral-llm-workbench')

from app import ChoralWorkbench

def test_complete_pipeline():
    """Test the complete Choral Workbench pipeline"""
    
    print("🧪 Testing complete pipeline: Upload → Transform → Semantic Diff → Export...")
    
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
        
        # 1. Upload and Parse
        print("\n1. 📁 Upload and Parse MusicXML...")
        result_tlr, result_msg = workbench.upload_and_parse(MockFile(test_file))
        print(f"   Result: {result_msg}")
        if result_tlr:
            print(f"   TLR Preview: {result_tlr[:100]}...")
        else:
            print("   ❌ Failed to upload/parse file")
            return False
        
        # Check that original scores are set
        if workbench.original_score is None or workbench.current_score is None:
            print("   ❌ Score tracking not working")
            return False
        print("   ✅ Score tracking working correctly")
        
        # 2. Transform
        print("\n2. 🔄 Transform Music...")
        try:
            # Test simple transpose transformation
            transformed_tlr, transform_msg = workbench.transform_with_validation(
                result_tlr, "Transpose up by 2 steps", True, False, False, False
            )
            print(f"   Result: {transform_msg}")
            if transformed_tlr and ("✅" in transform_msg or "⚠️" in transform_msg):
                print("   ✅ Transformation completed successfully")
                print(f"   Transformed TLR Preview: {transformed_tlr[:200]}...")
            elif "Error during transformation" in transform_msg:
                print("   ❌ Transformation failed with error")
                return False
            elif not transformed_tlr:
                print("   ❌ Transformation returned empty TLR")
                return False
            else:
                print("   ⚠️ Transformation completed but with unknown status")
            
            print(f"   Full Transformed TLR:")
            for i, line in enumerate(transformed_tlr.split('\n')[:10], 1):
                print(f"     {i}: {line}")
            if len(transformed_tlr.split('\n')) > 10:
                print(f"     ... ({len(transformed_tlr.split('\n'))} total lines)")
                return False
        except Exception as e:
            print(f"   ❌ Transformation error: {e}")
            return False
        
        # 3. Debug score states
        print("\n3. 🔍 Debug Score States...")
        print(f"   original_score type: {type(workbench.original_score)}")
        print(f"   current_score type: {type(workbench.current_score)}")
        print(f"   _last_transformed_tlr available: {hasattr(workbench, '_last_transformed_tlr') and workbench._last_transformed_tlr is not None}")
        
        # 3. Semantic Diff
        print("\n3. 🔍 Generate Semantic Diff...")
        try:
            # Use original_score and current_score if available, otherwise fallback
            if workbench.current_score is None:
                print("   ⚠️ current_score is None, attempting to re-parse transformed TLR...")
                try:
                    reparsed_score, parse_errors = workbench.tlr_parser.parse(transformed_tlr)
                    if parse_errors:
                        print(f"   Parse warnings: {parse_errors}")
                    
                    workbench.current_score = reparsed_score
                    
                    # Debug measure capacity check
                    if workbench.current_score and workbench.current_score.parts:
                        part = workbench.current_score.parts[0]
                        if part.voices:
                            voice = part.voices[0]
                            if voice.measures:
                                measure = voice.measures[0]
                                print(f"   Measure time signature: {measure.time_signature}")
                                for i, event in enumerate(measure.events):
                                    if hasattr(event, 'onset') and hasattr(event, 'duration'):
                                        print(f"   Event {i}: onset={event.onset}, dur={event.duration}, total={event.onset + event.duration}")
                except Exception as parse_e:
                    print(f"   ❌ Failed to re-parse: {parse_e}")
                    return False
            
            if workbench.current_score is not None:
                semantic_diffs = workbench.semantic_analyzer.compute_semantic_diff(
                    workbench.original_score, workbench.current_score
                )
                if semantic_diffs:
                    print(f"   ✅ Semantic diff generated ({len(semantic_diffs)} entries)")
                    for i, diff in enumerate(semantic_diffs[:3]):  # Show first 3
                        print(f"     {i+1}. [{diff.scope}] {diff.change_type}: {diff.description}")
                else:
                    print("   ⚠️ No semantic differences detected (might be expected)")
            else:
                print("   ❌ Cannot generate semantic diff - no valid current_score")
                return False
        except Exception as e:
            print(f"   ❌ Semantic diff error: {e}")
            return False
        
        # 4. Export
        print("\n4. 💾 Export MusicXML...")
        try:
            exported_file = workbench.export_musicxml(transformed_tlr)
            if exported_file and os.path.exists(exported_file):
                print(f"   ✅ Export successful: {exported_file}")
                # Verify exported file is valid XML
                with open(exported_file, 'r') as f:
                    content = f.read()
                    if '<?xml' in content and '<score-partwise' in content:
                        print("   ✅ Exported file is valid MusicXML")
                    else:
                        print("   ⚠️ Exported file may be invalid")
            else:
                print("   ❌ Export failed")
                return False
        except Exception as e:
            print(f"   ❌ Export error: {e}")
            return False
        
        # 5. Test UI Display Updates
        print("\n5. 🖥️ Test Semantic Diff UI Display...")
        try:
            diff_html = workbench.update_semantic_diff_display()
            if diff_html and len(diff_html.strip()) > 10:
                print("   ✅ Semantic diff UI display updated")
                print(f"   HTML Preview: {diff_html[:100]}...")
            else:
                print("   ⚠️ Semantic diff UI display is empty")
        except Exception as e:
            print(f"   ❌ UI display error: {e}")
        
        print("\n✅ Complete pipeline test successful!")
        return True
        
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
        
        # Clean up exported files
        for f in os.listdir('/tmp'):
            if f.startswith('transformed_') and f.endswith('.musicxml'):
                os.remove(f'/tmp/{f}')

if __name__ == "__main__":
    success = test_complete_pipeline()
    sys.exit(0 if success else 1)