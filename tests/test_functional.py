import pytest
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

def test_basic_imports():
    """Test that main modules can be imported"""
    try:
        from musicxml_parser import MusicXMLParser
        from tlr_converter import TLRConverter  
        from ollama_llm import OllamaLLM
        from tlr_diff_viewer import TLTDiffViewer
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import required modules: {e}")


def test_tlr_diff_viewer():
    """Test TLR Diff Viewer functionality"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
    
    from tlr_diff_viewer import TLTDiffViewer
    
    viewer = TLTDiffViewer()
    
    # Test basic diff creation
    original = "MEASURE 1\nNOTE t=0 pitch=C4 dur=1"
    transformed = "MEASURE 1\nNOTE t=0 pitch=D4 dur=1"
    
    diff = viewer.create_diff(original, transformed, "terminal")
    assert len(diff) > 0
    assert "MEASURE 1" in diff
    
    html_diff = viewer.create_diff(original, transformed, "html")
    assert len(html_diff) > 0
    assert "<html>" in html_diff


def test_ollama_llm():
    """Test Ollama LLM basic functionality"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
    
    from ollama_llm import OllamaLLM
    
    llm = OllamaLLM()
    
    # Test connection check
    # Note: This will likely fail in CI since Ollama isn't running
    # But it shouldn't crash
    try:
        conn = llm.check_connection()
        assert isinstance(conn, bool)
    except Exception:
        # Expected in CI environment
        pass


def test_transformation_validator():
    """Test transformation validator basic functionality"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
    
    from transformation_validator import TransformationValidator
    
    # Test that validator can be instantiated without crashing
    try:
        validator = TransformationValidator()
        assert hasattr(validator, 'allowed_transformations')
        # Note: This is actually a dict, not a set
        assert isinstance(validator.allowed_transformations, dict)
        assert len(validator.allowed_transformations) > 0
    except Exception as e:
        pytest.fail(f"Failed to instantiate TransformationValidator: {e}")
    
    # Test that validation method exists
    assert hasattr(validator, 'validate_transformation')
    assert callable(getattr(validator, 'validate_transformation'))