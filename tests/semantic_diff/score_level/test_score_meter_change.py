"""
Test for Meter Change Detection
Expected: [Score] Time signature changed: 4/4 → 3/4
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from semantic_diff_analyzer import SemanticDiffAnalyzer
from tests.fixtures.musicxml_fixture_generator import create_musicxml, prettify_xml, C4, E4, G4, A4


def test_score_meter_change():
    """Test detection of meter change from 4/4 to 3/4"""
    
    # Original 4/4 fixture
    original_parts = [
        ("Soprano", [
            ("4/4", [C4, E4, G4, A4]),        # 4 beats
        ]),
        ("Alto", [
            ("4/4", [A4, C4, E4, G4]),        # 4 beats
        ])
    ]
    
    # Transformed 3/4 fixture (same content, different meter)
    transformed_parts = [
        ("Soprano", [
            ("3/4", [C4, E4, G4]),              # 3 beats
        ]),
        ("Alto", [
            ("3/4", [A4, C4, E4]),              # 3 beats
        ])
    ]
    
    # Create and save fixtures
    fixtures_dir = Path(__file__).parent.parent.parent / "fixtures" / "musicxml"
    original_file = fixtures_dir / "original" / "meter_44_to_34.musicxml"
    transformed_file = fixtures_dir / "transformed" / "meter_44_to_34.musicxml"
    
    original_file.parent.mkdir(parents=True, exist_ok=True)
    transformed_file.parent.mkdir(parents=True, exist_ok=True)
    
    original_scorewise = create_musicxml(original_parts, "Original 4/4")
    transformed_scorewise = create_musicxml(transformed_parts, "Transformed 3/4")
    
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
    meter_change_found = False
    
    for diff in diffs:
        if 'meter' in diff.description.lower() or 'time' in diff.description.lower():
            meter_change_found = True
            print(f"✓ Meter change detected: {diff.description}")
    
    assert meter_change_found, "Meter change from 4/4 to 3/4 should be detected at score level"
    
    print(f"✓ Meter change test passed: {len(diffs)} differences found")
    return True


if __name__ == "__main__":
    test_score_meter_change()