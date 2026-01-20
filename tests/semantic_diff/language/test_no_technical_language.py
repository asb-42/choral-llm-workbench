"""
Test for Technical Language Guardrails
Tests that semantic diff output contains no forbidden technical terms
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from semantic_diff_analyzer import SemanticDiffAnalyzer
from tests.fixtures.musicxml_fixture_generator import create_musicxml, prettify_xml, C4, E4, G4


def test_no_technical_language():
    """Test that output contains no technical terms"""
    
    # Simple C major fixture
    parts = [
        ("Soprano", [
            ("4/4", [C4, E4, G4]),      # C major chord
        ])
    ]
    
    # Create MusicXML
    scorewise = create_musicxml(parts, "Technical Language Test")
    
    # Save fixture
    fixtures_dir = Path(__file__).parent.parent.parent / "fixtures" / "musicxml"
    original_file = fixtures_dir / "original" / "technical_test.musicxml"
    
    original_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(original_file, 'w') as f:
        f.write(prettify_xml(scorewise))
    
    # Test with same file (no changes) to see language
    analyzer = SemanticDiffAnalyzer()
    
    from musicxml_parser import MusicXMLParser
    parser = MusicXMLParser()
    
    score = parser.parse(str(original_file))
    diffs = analyzer.compute_semantic_diff(score, score)  # Same file, no changes
    
    # Forbidden patterns
    forbidden_patterns = [
        'duration=',           # Technical term
        'pitch=',             # Technical term
        'float',              # Programming term
        'IKRNode',           # Implementation detail
        'step=',              # Technical field
        'octave=',           # Technical field
        'alter=',             # Technical field
    ]
    
    # Collect all diff descriptions
    all_text = " ".join([diff.description for diff in diffs])
    
    # Check for forbidden patterns
    found_forbidden = []
    for pattern in forbidden_patterns:
        if pattern in all_text:
            found_forbidden.append(pattern)
            print(f"❌ Forbidden pattern found: {pattern}")
    
    # Test fails if any forbidden pattern is found
    if found_forbidden:
        print(f"❌ Test failed: Found forbidden patterns: {found_forbidden}")
        print(f"Diff output: {all_text}")
        assert False, f"Technical language detected: {found_forbidden}"
    else:
        print("✓ No technical language found")
        assert True, "No technical language should be present"
    
    print(f"✓ Technical language test passed: {len(diffs)} diffs checked")
    return True


if __name__ == "__main__":
    test_no_technical_language()