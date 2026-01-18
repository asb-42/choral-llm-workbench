import pytest
from tlr_diff_viewer import TLTDiffViewer
from ikr_light import Score, Part, Voice, Measure, NoteEvent
from fractions import Fraction


class TestTLTDiffViewer:
    """Test TLR diff viewer functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.diff_viewer = TLTDiffViewer()
    
    def test_terminal_diff_basic(self):
        """Test basic terminal diff creation"""
        original = """PART Test ROLE instrument
VOICE 1
MEASURE 1 TIME 4/4
NOTE t=0 dur=1/4 pitch=C4
NOTE t=1/4 dur=1/4 pitch=D4"""
        
        transformed = """PART Test ROLE instrument
VOICE 1
MEASURE 1 TIME 4/4
NOTE t=0 dur=1/4 pitch=E4
NOTE t=1/4 dur=1/4 pitch=D4"""
        
        diff = self.diff_viewer.create_diff(original, transformed, "terminal")
        
        assert "MEASURE 1" in diff
        assert "VOICE 1" in diff
        assert "+ NOTE t=0 dur=1/4 pitch=E4" in diff
        assert "- NOTE t=0 dur=1/4 pitch=C4" in diff
        assert "  NOTE t=1/4 dur=1/4 pitch=D4" in diff  # Unchanged line
    
    def test_html_diff_basic(self):
        """Test basic HTML diff creation"""
        original = """PART Test ROLE instrument
VOICE 1
MEASURE 1 TIME 4/4
NOTE t=0 dur=1/4 pitch=C4"""
        
        transformed = """PART Test ROLE instrument
VOICE 1
MEASURE 1 TIME 4/4
NOTE t=0 dur=1/4 pitch=E4"""
        
        diff = self.diff_viewer.create_diff(original, transformed, "html")
        
        assert "<!DOCTYPE html>" in diff
        assert "<title>TLR Diff Viewer</title>" in diff
        assert "class=\"measure-header\"" in diff
        assert "class=\"line-added\"" in diff
        assert "class=\"line-removed\"" in diff
        assert "NOTE t=0 dur=1/4 pitch=E4" in diff
        assert "NOTE t=0 dur=1/4 pitch=C4" in diff
    
    def test_plain_diff_basic(self):
        """Test plain text diff creation"""
        original = """PART Test ROLE instrument
MEASURE 1 TIME 4/4
NOTE t=0 dur=1/4 pitch=C4"""
        
        transformed = """PART Test ROLE instrument
MEASURE 1 TIME 4/4
NOTE t=0 dur=1/4 pitch=E4"""
        
        diff = self.diff_viewer.create_diff(original, transformed, "plain")
        
        assert "--- Original TLR" in diff
        assert "+++ Transformed TLR" in diff
        assert "-NOTE t=0 dur=1/4 pitch=C4" in diff
        assert "+NOTE t=0 dur=1/4 pitch=E4" in diff
    
    def test_structure_extraction(self):
        """Test structure extraction from TLR lines"""
        # Measure line
        measure, voice = self.diff_viewer._extract_structure_from_line("MEASURE 12 TIME 3/4")
        assert measure == 12
        assert voice is None
        
        # Voice line
        measure, voice = self.diff_viewer._extract_structure_from_line("VOICE 2")
        assert measure is None
        assert voice == "2"
        
        # Event line
        measure, voice = self.diff_viewer._extract_structure_from_line("NOTE t=0 dur=1/4 pitch=C4")
        assert measure is None
        assert voice is None
        
        # Complex line with both
        measure, voice = self.diff_viewer._extract_structure_from_line("MEASURE 8 TIME 6/8")
        assert measure == 8
        assert voice is None
    
    def test_event_line_detection(self):
        """Test event line detection"""
        assert self.diff_viewer._is_event_line("NOTE t=0 dur=1/4 pitch=C4")
        assert self.diff_viewer._is_event_line("REST t=0 dur=1/4")
        assert self.diff_viewer._is_event_line("HARMONY t=0 symbol=I")
        assert self.diff_viewer._is_event_line("LYRIC t=0 text=Hello")
        
        assert not self.diff_viewer._is_event_line("PART Test ROLE instrument")
        assert not self.diff_viewer._is_event_line("VOICE 1")
        assert not self.diff_viewer._is_event_line("MEASURE 1 TIME 4/4")
        assert not self.diff_viewer._is_event_line("")
    
    def test_diff_summary_creation(self):
        """Test diff summary statistics"""
        original_lines = [
            "PART Test ROLE instrument",
            "MEASURE 1 TIME 4/4", 
            "NOTE t=0 dur=1/4 pitch=C4",
            "NOTE t=1/4 dur=1/4 pitch=D4"
        ]
        
        # One event added, one changed
        transformed_lines = [
            "PART Test ROLE instrument",
            "MEASURE 1 TIME 4/4",
            "NOTE t=0 dur=1/4 pitch=E4",  # Changed
            "NOTE t=1/4 dur=1/4 pitch=D4",
            "NOTE t=1/2 dur=1/4 pitch=F4"   # Added
        ]
        
        summary = self.diff_viewer._create_diff_summary(original_lines, transformed_lines)
        
        assert "Changed: 1 events" in summary
        assert "Added: 1 events" in summary
    
    def test_no_changes_summary(self):
        """Test summary when no changes"""
        lines = [
            "PART Test ROLE instrument",
            "MEASURE 1 TIME 4/4", 
            "NOTE t=0 dur=1/4 pitch=C4"
        ]
        
        summary = self.diff_viewer._create_diff_summary(lines, lines)
        assert summary == "No changes detected"
    
    def test_measure_focused_diff(self):
        """Test measure-focused diff filtering"""
        original = """PART Test ROLE instrument
VOICE 1
MEASURE 1 TIME 4/4
NOTE t=0 dur=1/4 pitch=C4
NOTE t=1/4 dur=1/4 pitch=D4
MEASURE 2 TIME 4/4
NOTE t=0 dur=1/4 pitch=E4
NOTE t=1/4 dur=1/4 pitch=F4"""
        
        transformed = """PART Test ROLE instrument
VOICE 1
MEASURE 1 TIME 4/4
NOTE t=0 dur=1/4 pitch=G4
NOTE t=1/4 dur=1/4 pitch=D4
MEASURE 2 TIME 4/4
NOTE t=0 dur=1/4 pitch=E4
NOTE t=1/4 dur=1/4 pitch=F4"""
        
        # Focus on measure 1
        diff = self.diff_viewer.create_measure_focused_diff(original, transformed, 1, "terminal")
        
        assert "MEASURE 1" in diff
        assert "NOTE t=0 dur=1/4 pitch=G4" in diff  # Changed in measure 1
        assert "NOTE t=0 dur=1/4 pitch=E4" not in diff  # From measure 2, should be excluded
        assert "NOTE t=0 dur=1/4 pitch=F4" not in diff  # From measure 2, should be excluded
    
    def test_complex_diff_scenario(self):
        """Test complex diff scenario with multiple parts and voices"""
        original = """PART Soprano ROLE choir
VOICE 1
MEASURE 1 TIME 4/4
NOTE t=0 dur=1/4 pitch=C5
NOTE t=1/4 dur=1/4 pitch=D5
MEASURE 2 TIME 4/4
NOTE t=0 dur=1/2 pitch=E5

PART Alto ROLE choir
VOICE 1
MEASURE 1 TIME 4/4
NOTE t=0 dur=1/4 pitch=G4
NOTE t=1/4 dur=1/4 pitch=A4"""
        
        transformed = """PART Soprano ROLE choir
VOICE 1
MEASURE 1 TIME 4/4
NOTE t=0 dur=1/4 pitch=B4
NOTE t=1/4 dur=1/4 pitch=D5
MEASURE 2 TIME 4/4
NOTE t=0 dur=1/4 pitch=E5
NOTE t=1/4 dur=1/4 pitch=F5

PART Alto ROLE choir
VOICE 1
MEASURE 1 TIME 4/4
NOTE t=0 dur=1/4 pitch=G4
NOTE t=1/4 dur=1/4 pitch=A4"""
        
        diff = self.diff_viewer.create_diff(original, transformed, "terminal")
        
        # Check that structure is preserved
        assert "MEASURE 1" in diff
        assert "MEASURE 2" in diff
        assert "PART Soprano" in diff
        assert "PART Alto" in diff
        assert "VOICE 1" in diff
        
        # Check specific changes
        assert "- NOTE t=0 dur=1/4 pitch=C5" in diff
        assert "+ NOTE t=0 dur=1/4 pitch=B4" in diff
        assert "+ NOTE t=1/4 dur=1/4 pitch=F5" in diff  # Added in measure 2
        
        # Check unchanged lines
        assert "  NOTE t=1/4 dur=1/4 pitch=D5" in diff
        assert "  NOTE t=0 dur=1/2 pitch=E5" in diff
        assert "  NOTE t=0 dur=1/4 pitch=G4" in diff  # Alto unchanged
        assert "  NOTE t=1/4 dur=1/4 pitch=A4" in diff  # Alto unchanged
    
    def test_color_codes(self):
        """Test that color codes are properly defined"""
        assert 'removed' in self.diff_viewer.colors
        assert 'added' in self.diff_viewer.colors
        assert 'changed' in self.diff_viewer.colors
        assert 'measure_header' in self.diff_viewer.colors
        assert 'voice_header' in self.diff_viewer.colors
        assert 'reset' in self.diff_viewer.colors
        
        # Check HTML colors
        assert 'removed' in self.diff_viewer.html_colors
        assert 'added' in self.diff_viewer.html_colors
        assert 'changed' in self.diff_viewer.html_colors
        assert 'measure_header' in self.diff_viewer.html_colors
        assert 'voice_header' in self.diff_viewer.html_colors
        assert 'unchanged' in self.diff_viewer.html_colors