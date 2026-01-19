#!/usr/bin/env python3
"""
Quick End-to-End Test für die fixierte Pipeline
"""

import sys
import os
import time
sys.path.insert(0, '/home/asb/Projekte/choral-llm-workbench')

from app import ChoralWorkbench

def test_fixed_pipeline():
    """Test der kompletten Pipeline mit den Fixes"""
    
    print("🚀 TESTING FIXED PIPELINE")
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
    
    test_file = "/tmp/test_fixed.xml"
    with open(test_file, 'w') as f:
        f.write(test_musicxml)
    
    class MockFile:
        def __init__(self, name):
            self.name = name
    
    workbench = ChoralWorkbench()
    
    try:
        # 1. Upload
        print("1. 📁 Upload & Parse...")
        start_time = time.time()
        result_tlr, result_msg = workbench.upload_and_parse(MockFile(test_file))
        upload_time = time.time() - start_time
        print(f"   ⏱️  Upload Time: {upload_time:.1f}s")
        print(f"   📝 Result: {result_msg}")
        
        # Verify score tracking
        print(f"   🎯 original_score set: {workbench.original_score is not None}")
        print(f"   🎯 current_score set: {workbench.current_score is not None}")
        
        # 2. Transform mit qwen2:1.5b
        print("\n2. 🔄 Transform (fast model)...")
        start_time = time.time()
        transformed_tlr, transform_msg = workbench.transform_with_validation(
            result_tlr, "Transpose up 2 steps", True, False, False, False
        )
        transform_time = time.time() - start_time
        print(f"   ⏱️  Transform Time: {transform_time:.1f}s")
        print(f"   📝 Result: {transform_msg}")
        
        if transformed_tlr:
            print(f"   🎼 Transformed TLR Preview: {transformed_tlr[:150]}...")
        else:
            print("   ❌ No transformed TLR returned")
            return False
        
        # 3. Semantic Diff
        print("\n3. 🔍 Semantic Diff...")
        start_time = time.time()
        diff_html = workbench.update_semantic_diff_display()
        diff_time = time.time() - start_time
        print(f"   ⏱️  Diff Time: {diff_time:.1f}s")
        
        if "No semantic diff available" in diff_html:
            print("   ❌ Semantic diff failed - no diff available")
        else:
            print("   ✅ Semantic diff generated successfully")
            print(f"   📊 HTML Length: {len(diff_html)} chars")
        
        # 4. Export
        print("\n4. 💾 Export...")
        start_time = time.time()
        exported_file = workbench.export_musicxml(transformed_tlr)
        export_time = time.time() - start_time
        print(f"   ⏱️  Export Time: {export_time:.1f}s")
        
        if exported_file and os.path.exists(exported_file):
            print(f"   ✅ Export successful: {exported_file}")
        else:
            print("   ❌ Export failed")
            return False
        
        # 5. Summary
        total_time = upload_time + transform_time + diff_time + export_time
        print(f"\n📊 PERFORMANCE SUMMARY:")
        print(f"   Upload: {upload_time:.1f}s")
        print(f"   Transform: {transform_time:.1f}s")
        print(f"   Semantic Diff: {diff_time:.1f}s")
        print(f"   Export: {export_time:.1f}s")
        print(f"   Total: {total_time:.1f}s")
        
        if transform_time < 60:  # Should be under 1 minute now
            print("\n✅ SUCCESS: Pipeline completed quickly with small model!")
            return True
        else:
            print(f"\n⚠️  WARNING: Transform still taking {transform_time:.1f}s (should be <30s)")
            return False
    
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    success = test_fixed_pipeline()
    sys.exit(0 if success else 1)