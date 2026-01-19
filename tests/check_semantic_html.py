#!/usr/bin/env python3
"""
Check what the semantic diff HTML actually contains
"""

import sys
sys.path.insert(0, '/home/asb/Projekte/choral-llm-workbench')

from app import ChoralWorkbench

def check_semantic_html():
    """Check the actual HTML content from semantic diff"""
    
    print("🔍 CHECK: Semantic Diff HTML Content")
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
    
    test_file = "/tmp/check_semantic.xml"
    with open(test_file, 'w') as f:
        f.write(test_musicxml)
    
    class MockFile:
        def __init__(self, name):
            self.name = name
    
    workbench = ChoralWorkbench()
    
    try:
        # Upload & Transform
        result_tlr, _ = workbench.upload_and_parse(MockFile(test_file))
        transformed_tlr, _ = workbench.transform_with_validation(
            result_tlr, "Transpose up 1 step", True, False, False, False
        )
        
        # Get semantic diff HTML
        html_output = workbench.update_semantic_diff_display()
        
        print("Full HTML Output:")
        print("=" * 30)
        print(html_output)
        print("=" * 30)
        
        # Check for key markers
        if "📝 System Changes" in html_output:
            print("✅ Contains 'System Changes' marker")
        else:
            print("❌ Missing 'System Changes' marker")
            
        if "🎼 Show musical changes" in html_output:
            print("✅ Contains 'Show musical changes' marker")
        else:
            print("❌ Missing 'Show musical changes' marker")
        
        # Look for actual diff content
        if "Pitch changed" in html_output:
            print("✅ Contains actual pitch changes")
        else:
            print("❌ No pitch changes found")
    
    finally:
        if hasattr(workbench, 'output_file') and workbench.output_file:
            import os
            if os.path.exists(workbench.output_file):
                os.unlink(workbench.output_file)

if __name__ == "__main__":
    check_semantic_html()