"""
Test for Deterministic Output
Same inputs should produce identical diff results
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from semantic_diff_analyzer import SemanticDiffAnalyzer
from tests.fixtures.musicxml_fixture_generator import create_musicxml, prettify_xml, C4, E4, G4


def test_deterministic_output():
    """Test that same inputs produce identical outputs"""
    
    # Simple C major fixture
    parts = [
        ("Soprano", [
            ("4/4", [C4, E4, G4]),      # C major chord
        ])
    ]
    
    # Create MusicXML
    scorewise = create_musicxml(parts, "Deterministic Test")
    
    # Save fixture
    fixtures_dir = Path(__file__).parent.parent.parent / "fixtures" / "musicxml"
    original_file = fixtures_dir / "original" / "deterministic.musicxml"
    
    original_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(original_file, 'w') as f:
        f.write(prettify_xml(scorewise))
    
    # Parse once
    analyzer = SemanticDiffAnalyzer()
    
    from musicxml_parser import MusicXMLParser
    parser = MusicXMLParser()
    
    score = parser.parse(str(original_file))
    
    # Run diff twice with same inputs
    diffs_1 = analyzer.compute_semantic_diff(score, score)  # Same file, no changes
    diffs_2 = analyzer.compute_semantic_diff(score, score)  # Same file, no changes
    
    # Convert to strings for comparison
    result_1 = " ".join([f"{diff.scope}:{diff.change_type}:{diff.description}" for diff in diffs_1])
    result_2 = " ".join([f"{diff.scope}:{diff.change_type}:{diff.description}" for diff in diffs_2])
    
    print(f"Run 1 result: {result_1}")
    print(f"Run 2 result: {result_2}")
    
    # Test deterministic output
    assert result_1 == result_2, f"Output should be deterministic. Run1: {result_1}, Run2: {result_2}"
    
    print(f"✓ Deterministic test passed: both runs produced identical results")
    return True


if __name__ == "__main__":
    test_deterministic_output()