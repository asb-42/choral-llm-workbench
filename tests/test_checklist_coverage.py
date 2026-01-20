"""
Test Suite Runner
Maps IKR Semantic Diff Checklist to tests and provides coverage reporting
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_checklist_coverage():
    """Ensure all checklist categories have corresponding tests"""
    
    # Checklist mapping to test modules
    checklist_to_tests = {
        # Score Level
        "A1 Score Key Change": "tests.semantic_diff.score_level.test_score_key_change",
        "A2 Global Transposition": "tests.semantic_diff.score_level.test_score_global_transposition", 
        "A3 Score Meter Change": "tests.semantic_diff.score_level.test_score_meter_change",
        "A4 Score Tempo Change": "tests.semantic_diff.score_level.test_score_tempo_change",
        
        # Voice Level
        "B1 Voice Transposition": "tests.semantic_diff.voice_level.test_voice_transposition_grouping",
        "B2 Voice Rhythm Simplification": "tests.semantic_diff.voice_level.test_voice_rhythm_simplification",
        
        # Event Level
        "C1 Event Duration Language": "tests.semantic_diff.event_level.test_event_duration_language",
        "C2 Event Interval Language": "tests.semantic_diff.event_level.test_event_interval_language",
        
        # Grouping & Summary
        "D1 Summary Block Exists": "tests.semantic_diff.grouping.test_summary_block",
        "D2 Summary Content Correctness": "tests.semantic_diff.grouping.test_summary_content",
        "D3 Summary Omitted on No-Op": "tests.semantic_diff.grouping.test_summary_noop",
        
        # Language & UX Constraints
        "E1 No Technical Terms": "tests.semantic_diff.language.test_no_technical_language",
        "E2 One Concept Per Line": "tests.semantic_diff.language.test_one_concept_per_line",
        
        # Negative / Guardrail Tests
        "F1 Layout Changes Ignored": "tests.semantic_diff.negative_cases.test_ignore_layout_changes",
        "F2 Deterministic Output": "tests.semantic_diff.negative_cases.test_deterministic_output",
    }
    
    # Import test modules to verify they exist
    missing_tests = []
    
    for checklist_item, test_module in checklist_to_tests.items():
        try:
            # Try to import the module
            module_parts = test_module.split('.')
            module = __import__(module_parts[0])
            
            # Navigate to the specific test function
            for part in module_parts[1:]:
                module = getattr(module, part)
            
            # Check if test function exists
            test_functions = [attr for attr in dir(module) if attr.startswith('test_')]
            if not test_functions:
                missing_tests.append(f"{checklist_item}: No test functions found in {test_module}")
            
        except ImportError as e:
            missing_tests.append(f"{checklist_item}: Cannot import {test_module} - {e}")
        except Exception as e:
            missing_tests.append(f"{checklist_item}: Error checking {test_module} - {e}")
    
    # Print coverage report
    total_checklist_items = len(checklist_to_tests)
    found_tests = total_checklist_items - len(missing_tests)
    coverage_percent = (found_tests / total_checklist_items) * 100
    
    print(f"\\n=== IKR Semantic Diff Coverage Report ===")
    print(f"Total Checklist Items: {total_checklist_items}")
    print(f"Implemented Tests: {found_tests}")
    print(f"Missing Tests: {len(missing_tests)}")
    print(f"Coverage: {coverage_percent:.1f}%")
    
    if missing_tests:
        print(f"\\n=== Missing Tests ===")
        for missing in missing_tests:
            print(f"❌ {missing}")
        assert False, f"Missing {len(missing_tests)} test implementations"
    else:
        print("✅ All checklist items have corresponding tests!")
        assert True, "All checklist items have test implementations"


if __name__ == "__main__":
    test_checklist_coverage()