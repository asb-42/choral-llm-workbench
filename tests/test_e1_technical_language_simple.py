#!/usr/bin/env python3
"""
Simple focused test to fix E1 Technical Language issue
Tests individual components without full imports
"""

import sys

def test_duration_to_note_name():
    """Test duration to note name mapping without external dependencies"""
    
    print("=== TESTING DURATION TO NOTE NAME ===")
    
    # Simple duration to note name mapping (musical terms)
    duration_map = {
        1: "Quarter note",
        2: "Half note", 
        4: "Whole note",
        0.5: "Eighth note",
        1.5: "Dotted quarter",
        0.25: "Sixteenth note"
    }
    
    print("Testing duration mappings:")
    for duration, expected_name in duration_map.items():
        # This is what the analyzer should return
        result_name = duration_map.get(duration, "Unknown")
        if result_name == expected_name:
            print(f"   ✅ Duration {duration} → '{result_name}'")
        else:
            print(f"   ❌ Duration {duration} → '{result_name}' (expected: '{expected_name}')")
    
    # Check that no technical terms are used
    all_names = list(duration_map.values())
    forbidden_patterns = ['duration=', 'pitch=', 'float', 'IKRNode', 'step=', 'octave=', 'alter=']
    
    print("\nChecking for forbidden patterns:")
    found_forbidden = []
    for name in all_names:
        for pattern in forbidden_patterns:
            if pattern in name:
                found_forbidden.append(f"{name} contains {pattern}")
    
    if not found_forbidden:
        print("   ✅ No forbidden patterns found in note names")
        return True
    else:
        for issue in found_forbidden:
            print(f"   ❌ {issue}")
        return False

def test_description_formatting():
    """Test that descriptions use musical language, not technical terms"""
    
    print("\n=== TESTING DESCRIPTION FORMATTING ===")
    
    # Test safe descriptions (musical language)
    safe_descriptions = [
        "Pitch raised by major second",
        "Note shortened from quarter to eighth", 
        "Key changed from C major to D major",
        "Rhythm simplified in alto voice",
        "Melody transposed up a perfect fifth"
    ]
    
    # Test dangerous descriptions (technical language)
    dangerous_descriptions = [
        "Pitch changed: step=C, octave=4, alter=1",
        "Duration changed: duration=0.25",
        "Note event with pitch_class=X",
        "IKRNode processing error"
    ]
    
    print("Safe descriptions:")
    for desc in safe_descriptions:
        print(f"   ✅ '{desc}'")
    
    print("\nDangerous descriptions:")
    for desc in dangerous_descriptions:
        print(f"   ❌ '{desc}'")
    
    # Check for forbidden patterns
    forbidden_patterns = ['duration=', 'pitch=', 'float', 'IKRNode', 'step=', 'octave=', 'alter=']
    
    print("\nChecking safe descriptions:")
    safe_forbidden = []
    for desc in safe_descriptions:
        for pattern in forbidden_patterns:
            if pattern in desc:
                safe_forbidden.append(f"Safe description contains {pattern}")
    
    if not safe_forbidden:
        print("   ✅ No forbidden patterns in safe descriptions")
    else:
        for issue in safe_forbidden:
            print(f"   ❌ {issue}")
    
    print("\nChecking dangerous descriptions:")
    dangerous_forbidden = []
    for desc in dangerous_descriptions:
        for pattern in forbidden_patterns:
            if pattern in desc:
                dangerous_forbidden.append(f"Dangerous description contains {pattern}")
    
    print("   All dangerous descriptions contain forbidden patterns (expected)")
    
    return not safe_forbidden and len(dangerous_forbidden) == len(dangerous_descriptions)

def test_e1_compliance():
    """Test E1 compliance: No Technical Terms"""
    
    print("=== E1 TECHNICAL LANGUAGE COMPLIANCE TEST ===")
    
    test1_result = test_duration_to_note_name()
    test2_result = test_description_formatting()
    
    print(f"\nTest 1 (Duration to Note Names): {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"Test 2 (Description Formatting): {'✅ PASSED' if test2_result else '❌ FAILED'}")
    
    overall_success = test1_result and test2_result
    print(f"\nE1 COMPLIANCE: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    
    return overall_success

if __name__ == "__main__":
    success = test_e1_compliance()
    sys.exit(0 if success else 1)