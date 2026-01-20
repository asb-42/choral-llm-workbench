"""
Test for Score-Level Key Change Detection
Original: C major
Transformed: D major
Expected: [Score] Key changed: C major → D major
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from semantic_diff_analyzer import SemanticDiffAnalyzer
from tests.fixtures.musicxml_fixture_generator import create_musicxml, prettify_xml, C4, D4, E4, F4, G4, A4, B4, C5, F4_sharp


def test_score_key_change():
    """Test detection of key change between C major and D major"""
    
    # Create C major fixture (simple chord progression)
    original_parts = [
        ("Soprano", [
            ("4/4", [C4, E4, G4]),      # C major chord
            ("4/4", [F4, A4, C5]),  # F major chord
            ("4/4", [G4, B4, D4]),      # G major chord
        ]),
        ("Alto", [
            ("4/4", [C4, E4, G4]),      # C major chord
            ("4/4", [F4, A4, C5]),  # F major chord
            ("4/4", [G4, B4, D4]),      # G major chord
        ])
    ]
    
    # Create D major fixture (same structure, transposed up 2 semitones)
    transformed_parts = [
        ("Soprano", [
            ("4/4", [D4, F4_sharp, A4]),  # D major chord (+2 semitones)
            ("4/4", [G4, B4, E4]),      # G major chord (+2 semitones)  
            ("4/4", [A4, C5, F4_sharp]), # A major chord (+2 semitones)
        ]),
        ("Alto", [
            ("4/4", [D4, F4_sharp, A4]),  # D major chord (+2 semitones)
            ("4/4", [G4, B4, E4]),      # G major chord (+2 semitones)  
            ("4/4", [A4, C5, F4_sharp]), # A major chord (+2 semitones)
        ])
    ]
    
    # Create MusicXML files
    original_scorewise = create_musicxml(original_parts, "C Major Test")
    transformed_scorewise = create_musicxml(transformed_parts, "D Major Test")
    
    # Save fixtures
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "musicxml"
    original_file = fixtures_dir / "original" / "key_change_c_to_d.musicxml"
    transformed_file = fixtures_dir / "transformed" / "key_change_c_to_d.musicxml"
    
    original_file.parent.mkdir(parents=True, exist_ok=True)
    transformed_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(original_file, 'w') as f:
        f.write(prettify_xml(original_scorewise))
    
    with open(transformed_file, 'w') as f:
        f.write(prettify_xml(transformed_scorewise))
    
    # Test semantic diff
    analyzer = SemanticDiffAnalyzer()
    
    # Parse files using existing parser
    from musicxml_parser import MusicXMLParser
    parser = MusicXMLParser()
    
    original_score = parser.parse(str(original_file))
    transformed_score = parser.parse(str(transformed_file))
    
    # Analyze differences
    diffs = analyzer.compute_semantic_diff(original_score, transformed_score)
    
    # Assertions
    key_change_found = False
    pitch_change_found = False
    
    for diff in diffs:
        if 'key' in diff.description.lower():
            key_change_found = True
            print(f"✓ Key change detected: {diff.description}")
        
        if 'pitch' in diff.scope.lower():
            pitch_change_found = True
            print(f"❌ Individual pitch change found: {diff.description}")
    
    # Verify key change was detected
    assert key_change_found, "Key change from C to D should be detected at score level"
    
    # Negative assertion: Should not show individual pitch changes for transposition
    assert not pitch_change_found, "Global transposition should not be reported as individual pitch changes"
    
    print(f"✓ Test passed: {len(diffs)} semantic differences found")
    return True


if __name__ == "__main__":
    test_score_key_change()