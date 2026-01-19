#!/usr/bin/env python3
"""
Debug Export Function
"""

import sys
import os
import tempfile
sys.path.insert(0, '/home/asb/Projekte/choral-llm-workbench')

from app import ChoralWorkbench

def debug_export():
    """Debug why export is failing"""
    
    print("🔍 DEBUG: Export Function")
    print("=" * 40)
    
    # Test TLR (transformed result from previous test)
    test_tlr = """PART Piano ROLE instrument
VOICE 1
MEASURE 1 TIME 4/4
NOTE t=0 dur=1 pitch=C#4
NOTE t=1 dur=1 pitch=D#4
NOTE t=2 dur=1 pitch=E4
NOTE t=3 dur=1 pitch=F4"""
    
    workbench = ChoralWorkbench()
    
    print("1. Testing export_musicxml with transformed TLR...")
    try:
        exported_file = workbench.export_musicxml(test_tlr)
        print(f"   Returned: {exported_file}")
        print(f"   Type: {type(exported_file)}")
        
        if exported_file:
            print(f"   Exists: {os.path.exists(exported_file)}")
            if os.path.exists(exported_file):
                print(f"   Size: {os.path.getsize(exported_file)} bytes")
                with open(exported_file, 'r') as f:
                    content = f.read()
                    print(f"   Content preview: {content[:200]}...")
            else:
                print("   ❌ File doesn't exist")
        else:
            print("   ❌ export_musicxml returned None/empty")
    
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n2. Testing TLR parsing before export...")
    try:
        parsed_score, parse_errors = workbench.tlr_parser.parse(test_tlr)
        print(f"   Parsed score: {parsed_score is not None}")
        print(f"   Parse errors: {parse_errors}")
        
        if parsed_score:
            print(f"   Parts: {len(parsed_score.parts)}")
            if parsed_score.parts:
                part = parsed_score.parts[0]
                print(f"   Part name: {part.name}")
                print(f"   Part voices: {len(part.voices)}")
    except Exception as e:
        print(f"   ❌ Parse exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n3. Testing musicxml_exporter directly...")
    try:
        if workbench.current_score:
            result_file = workbench.musicxml_exporter.export_musicxml(workbench.current_score)
            print(f"   Direct export result: {result_file}")
            if result_file and os.path.exists(result_file):
                print(f"   Direct export success: {os.path.getsize(result_file)} bytes")
        else:
            print("   ❌ No current_score available for direct export")
    except Exception as e:
        print(f"   ❌ Direct export exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_export()