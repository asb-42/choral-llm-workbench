#!/usr/bin/env python3
"""
Test Runner for Choral LLM Workbench
Usage: python run_tests.py [--unit] [--property] [--negative] [--all]
"""

import sys
import subprocess
import os


def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    print(f"Return code: {result.returncode}")
    
    return result.returncode == 0


def main():
    """Main test runner"""
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("Error: pytest not found. Please install with:")
        print("pip install -r test-requirements.txt")
        sys.exit(1)
    
    # Parse command line arguments
    args = sys.argv[1:]
    
    if not args or "--all" in args:
        # Run all tests
        tests = [
            ("python -m pytest tests/test_roundtrip_fixed.py -v", "Roundtrip Unit Tests"),
            ("python -m pytest tests/test_property_negative.py::TestPropertyBased -v", "Property-Based Tests"),
            ("python -m pytest tests/test_property_negative.py::TestNegativeTests -v", "Negative Tests"),
            ("python -m pytest tests/test_helmholtz.py -v", "Helmholtz Notation Tests"),
            ("python -m pytest tests/test_harmony.py -v", "Harmony Events Tests"),
            ("python -m pytest tests/test_explainer.py -v", "Explainer Mode Tests"),
            ("python -m pytest tests/test_transformation_validator.py -v", "Transformation Validator Tests"),
            ("python -m pytest tests/test_tlr_diff_viewer.py -v", "TLR Diff Viewer Tests"),
        ]
    else:
        tests = []
        
        if "--unit" in args:
            tests.append(("python -m pytest tests/test_roundtrip_fixed.py -v", "Roundtrip Unit Tests"))
        
        if "--property" in args:
            tests.append(("python -m pytest tests/test_property_negative.py::TestPropertyBased -v", "Property-Based Tests"))
        
        if "--negative" in args:
            tests.append(("python -m pytest tests/test_property_negative.py::TestNegativeTests -v", "Negative Tests"))
        
        if "--helmholtz" in args:
            tests.append(("python -m pytest tests/test_helmholtz.py -v", "Helmholtz Notation Tests"))
        
        if "--harmony" in args:
            tests.append(("python -m pytest tests/test_harmony.py -v", "Harmony Events Tests"))
        
        if "--explain" in args:
            tests.append(("python -m pytest tests/test_explainer.py -v", "Explainer Mode Tests"))
        
        if "--validator" in args:
            tests.append(("python -m pytest tests/test_transformation_validator.py -v", "Transformation Validator Tests"))
        
        if "--diff" in args:
            tests.append(("python -m pytest tests/test_tlr_diff_viewer.py -v", "TLR Diff Viewer Tests"))
    
    if not tests:
        print("Usage: python run_tests.py [--unit] [--property] [--negative] [--all]")
        sys.exit(1)
    
    # Run tests and track results
    results = []
    
    for cmd, description in tests:
        success = run_command(cmd, description)
        results.append((description, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    all_passed = True
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status:8} {description}")
        if not success:
            all_passed = False
    
    print(f"{'='*60}")
    if all_passed:
        print("🎉 ALL TESTS PASSED! Confidence: HIGH")
        sys.exit(0)
    else:
        print("⚠️  SOME TESTS FAILED! Confidence: LOW")
        sys.exit(1)


if __name__ == "__main__":
    main()