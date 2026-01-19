#!/usr/bin/env python3
"""
Debug Script für LLM Timeout Issues
Testet verschiedene Konfigurationen und Prompts
"""

import sys
import os
import time
sys.path.insert(0, '/home/asb/Projekte/choral-llm-workbench')

from app import ChoralWorkbench

def test_llm_performance():
    """Test LLM performance mit verschiedenen Konfigurationen"""
    
    print("🔍 DEBUG: LLM Performance Analyse")
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
    
    test_file = "/tmp/test_debug.xml"
    with open(test_file, 'w') as f:
        f.write(test_musicxml)
    
    class MockFile:
        def __init__(self, name):
            self.name = name
    
    workbench = ChoralWorkbench()
    
    try:
        # 1. Upload und TLR parsen
        print("1. 📁 Upload & Parse...")
        result_tlr, result_msg = workbench.upload_and_parse(MockFile(test_file))
        print(f"   TLR: {result_tlr[:100]}...")
        
        # 2. Test verschiedene Modelle
        print("\n2. 🤖 Teste Modelle...")
        models_to_test = ["mistral:latest", "llama3:latest"]
        
        for model in models_to_test:
            print(f"\n   Teste Modell: {model}")
            workbench.llm.set_model(model)
            
            # Einfacher Test ohne transformation_constraints
            print(f"   📊 Einfacher Prompt Test...")
            start_time = time.time()
            try:
                response = workbench.llm._call_ollama(
                    "Transform music. OUTPUT ONLY TLR format: PART Piano ROLE instrument\\nVOICE 1\\nMEASURE 1 TIME 4/4\\nNOTE t=0 dur=1 pitch=D4\\nNOTE t=1 dur=1 pitch=E4",
                    f"{result_tlr}\\n\\nInstruction: Transpose up 1 step",
                    timeout=120  # 2 Minuten
                )
                elapsed = time.time() - start_time
                print(f"   ✅ Erfolgreich in {elapsed:.1f}s")
                print(f"   Response: {response[:100]}...")
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"   ❌ Fehler nach {elapsed:.1f}s: {e}")
        
        # 3. Test mit transformation_constraints
        print("\n3. 🔧 Test mit Transformation Constraints...")
        workbench.llm.set_model("mistral:latest")  #回到默认模型
        
        start_time = time.time()
        try:
            # Simuliere die enhance_prompts wie in transform_with_validation
            allowed_flags = {'transpose'}
            transformation_constraints = workbench.transformation_validator.get_transformation_prompt_additions(allowed_flags)
            enhanced_system_prompt = workbench.llm.system_prompt + "\n" + transformation_constraints
            
            print(f"   System Prompt Length: {len(enhanced_system_prompt)} chars")
            print(f"   Transformation Constraints: {transformation_constraints[:100]}...")
            
            response = workbench.llm._call_ollama(
                enhanced_system_prompt,
                f"{result_tlr}\\n\\nInstruction: Transpose up 1 step",
                timeout=180  # 3 Minuten
            )
            elapsed = time.time() - start_time
            print(f"   ✅ Erfolgreich in {elapsed:.1f}s")
            print(f"   Response: {response[:100]}...")
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   ❌ Fehler nach {elapsed:.1f}s: {e}")
        
        # 4. Test mit sehr kleinem Input
        print("\n4. 🧪 Test mit minimalem Input...")
        minimal_tlr = "PART Piano ROLE instrument\\nVOICE 1\\nMEASURE 1 TIME 4/4\\nNOTE t=0 dur=1 pitch=C4"
        
        start_time = time.time()
        try:
            response = workbench.llm._call_ollama(
                "Transpose music. OUTPUT ONLY TLR.",
                f"{minimal_tlr}\\n\\nInstruction: Transpose up 1 step",
                timeout=60
            )
            elapsed = time.time() - start_time
            print(f"   ✅ Erfolgreich in {elapsed:.1f}s")
            print(f"   Response: {response[:100]}...")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   ❌ Fehler nach {elapsed:.1f}s: {e}")
    
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test_llm_performance()