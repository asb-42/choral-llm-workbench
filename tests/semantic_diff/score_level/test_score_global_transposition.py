"""
Test for Global Transposition vs Key Change
Should detect transposition (+2 semitones) not individual pitch changes
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from semantic_diff_analyzer import SemanticDiffAnalyzer
from tests.fixtures.musicxml_fixture_generator import (
    create_musicxml, prettify_xml, C4, D4, E4, F4, G4, A4, B4, C5, F4_sharp
)


def test_score_global_transposition():
    """Test that global transposition is detected correctly"""
    
    # Original C major progression
    original_parts = [
        ("Soprano", [
            ("4/4", [C4, E4, G4]),        # C major chord
            ("4/4", [F4, A4, C5]),    # F major chord  
            ("4/4", [G4, B4, D4]),        # G major chord
        ]),
        ("Alto", [
            ("4/4", [C4, E4, G4]),        # C major chord
            ("4/4", [F4, A4, C5]),    # F major chord
            ("4/4", [G4, B4, D4]),        # G major chord
        ])
    ]
    
    # Transposed D major progression (+2 semitones)
    transformed_parts = [
        ("Soprano", [
            ("4/4", [D4, F4_sharp, A4]),      # D major chord (+2)
            ("4/4", [G4, B4, E4]),            # G major chord (+2)
            ("4/4", [A4, C5, F4_sharp]),      # A major chord (+2)
        ]),
        ("Alto", [
            ("4/4", [D4, F4_sharp, A4]),      # D major chord (+2)
            ("4/4", [G4, B4, E4]),            # G major chord (+2)
            ("4/4", [A4, C5, F4_sharp]),      # A major chord (+2)
        ])
    ]
    
    # Create and save fixtures
    fixtures_dir = Path(__file__).parent.parent.parent / "fixtures" / "musicxml"
    original_file = fixtures_dir / "original" / "global_transposition.musicxml"
    transformed_file = fixtures_dir / "transformed" / "global_transposition_up2.musicxml"
    
    original_file.parent.mkdir(parents=True, exist_ok=True)
    transformed_file.parent.mkdir(parents=True, exist_ok=True)
    
    original_scorewise = create_musicxml(original_parts, "Original - C Major")
    transformed_scorewise = create_musicxml(transformed_parts, "Transposed - D Major")
    
    with open(original_file, 'w') as f:
        f.write(prettify_xml(original_scorewise))
    
    with open(transformed_file, 'w') as f:
        f.write(prettify_xml(transformed_scorewise))
    
    # Analyze
    analyzer = SemanticDiffAnalyzer()
    
    from musicxml_parser import MusicXMLParser
    parser = MusicXMLParser()
    
    original_score = parser.parse(str(original_file))
    transformed_score = parser.parse(str(transformed_file))
    
    diffs = analyzer.compute_semantic_diff(original_score, transformed_score)
    
    # Assertions
    transposition_found = False
    pitch_change_found = False
    
    for diff in diffs:
        if 'transposition' in diff.description.lower():
            transposition_found = True
            print(f"✓ Transposition detected: {diff.description}")
        
        if 'pitch' in diff.scope.lower() and 'note' in diff.scope.lower():
            pitch_change_found = True
            print(f"❌ Individual pitch change: {diff.description}")
    
    # Should detect transposition at score level
    assert transposition_found, "Global transposition should be detected at score level"
    
    # Should NOT detect individual pitch changes
    assert not pitch_change_found, "Global transposition should not be reported as individual pitch changes"
    
    print(f"✓ Global transposition test passed: {len(diffs)} differences found")
    return True


if __name__ == "__main__":
    test_score_global_transposition()