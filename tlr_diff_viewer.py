from typing import List, Dict, Tuple, Optional
import difflib
from ikr_light import Score, Event, NoteEvent


class TLTDiffViewer:
    """Text-based diff viewer for TLR changes with measure/voice highlighting"""
    
    def __init__(self):
        self.colors = {
            'removed': '\033[91m',    # Red background
            'added': '\033[92m',      # Green background  
            'changed': '\033[93m',    # Yellow background
            'measure_header': '\033[94m',  # Blue background
            'voice_header': '\033[95m',  # Magenta background
            'reset': '\033[0m'        # Reset
        }
        
        # For HTML output - improved contrast
        self.html_colors = {
            'removed': '#ffebee',      # Light red background
            'added': '#e8f5e8',       # Light green background  
            'changed': '#fff3e0',       # Light orange background
            'measure_header': '#e3f2fd', # Light blue background
            'voice_header': '#fce4ec',    # Light pink background
            'unchanged': '#fafafa',      # Very light gray background
            'text_removed': '#d32f2f',    # Dark red text
            'text_added': '#2e7d32',      # Dark green text
            'text_changed': '#f57c00',    # Dark orange text
            'text_header': '#1565c0',     # Dark blue text
            'text_normal': '#212121'       # Dark gray text
        }
    
    def create_diff(self, original_tlr: str, transformed_tlr: str, 
                   format_type: str = "terminal") -> str:
        """
        Create diff between original and transformed TLR
        
        Args:
            original_tlr: Original TLR text
            transformed_tlr: Transformed TLR text  
            format_type: "terminal" or "html"
        
        Returns:
            Formatted diff string
        """
        if format_type == "terminal":
            return self._create_terminal_diff(original_tlr, transformed_tlr)
        elif format_type == "html":
            return self._create_html_diff(original_tlr, transformed_tlr)
        else:
            return self._create_plain_diff(original_tlr, transformed_tlr)
    
    def _create_terminal_diff(self, original_tlr: str, transformed_tlr: str) -> str:
        """Create terminal-based diff with color highlighting"""
        original_lines = original_tlr.splitlines()
        transformed_lines = transformed_tlr.splitlines()
        
        # Create line-by-line diff
        differ = difflib.Differ()
        diff_lines = list(differ.compare(original_lines, transformed_lines))
        
        # Group lines by measure and voice
        grouped_lines = self._group_lines_by_structure(diff_lines)
        
        # Build formatted output
        result = []
        result.append(self.colors['measure_header'] + "=== TLR DIFF VIEW ====" + self.colors['reset'])
        result.append("")
        
        current_measure = None
        current_voice = None
        
        for line_group in grouped_lines:
            line_type, content, measure, voice = line_group
            
            # Show measure/voice headers
            if measure != current_measure:
                current_measure = measure
                result.append("")
                result.append(self.colors['measure_header'] + f"MEASURE {measure}" + self.colors['reset'])
            
            if voice != current_voice and voice:
                current_voice = voice
                result.append(self.colors['voice_header'] + f"  VOICE {voice}" + self.colors['reset'])
            
            # Format the line
            formatted_line = self._format_diff_line_terminal(line_type, content)
            if formatted_line:
                result.append(formatted_line)
        
        # Add summary
        summary = self._create_diff_summary(original_lines, transformed_lines)
        result.append("")
        result.append(self.colors['measure_header'] + "=== SUMMARY ====" + self.colors['reset'])
        result.append(summary)
        
        return "\n".join(result)
    
    def _create_html_diff(self, original_tlr: str, transformed_tlr: str) -> str:
        """Create HTML-based diff with color highlighting"""
        original_lines = original_tlr.splitlines()
        transformed_lines = transformed_tlr.splitlines()
        
        # Create line-by-line diff
        differ = difflib.Differ()
        diff_lines = list(differ.compare(original_lines, transformed_lines))
        
        # Group lines by measure and voice
        grouped_lines = self._group_lines_by_structure(diff_lines)
        
        # Build HTML output
        html_parts = []
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html>")
        html_parts.append("<head>")
        html_parts.append('<meta charset="UTF-8">')
        html_parts.append("<title>TLR Diff Viewer</title>")
        html_parts.append("<style>")
        html_parts.append("""
            body { font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.4; margin: 20px; background-color: #fafafa; }
            .diff-container { border: 1px solid #ddd; border-radius: 8px; padding: 20px; background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .measure-header { background-color: #e3f2fd; color: #1565c0; font-weight: bold; padding: 8px 12px; margin-top: 15px; border-radius: 4px; border-left: 4px solid #1976d2; }
            .voice-header { background-color: #fce4ec; color: #880e4f; padding: 6px 12px; margin: 8px 0; border-radius: 4px; border-left: 3px solid #c2185b; }
            .line-added { background-color: #e8f5e8; color: #2e7d32; padding: 2px 8px; border-left: 3px solid #4caf50; }
            .line-removed { background-color: #ffebee; color: #d32f2f; text-decoration: line-through; padding: 2px 8px; border-left: 3px solid #f44336; }
            .line-changed { background-color: #fff3e0; color: #f57c00; padding: 2px 8px; border-left: 3px solid #ff9800; }
            .line-unchanged { background-color: #fafafa; color: #212121; padding: 2px 8px; }
            .line-number { color: #757575; width: 40px; display: inline-block; font-weight: bold; }
            .summary { background-color: #f5f5f5; color: #424242; padding: 15px; border-radius: 6px; margin-top: 20px; border: 1px solid #e0e0e0; }
        """)
        html_parts.append("</style>")
        html_parts.append("</head>")
        html_parts.append("<body>")
        html_parts.append('<div class="diff-container">')
        html_parts.append("<h2>TLR Diff Viewer</h2>")
        
        current_measure = None
        current_voice = None
        line_number = 1
        
        for line_group in grouped_lines:
            line_type, content, measure, voice = line_group
            
            # Show measure/voice headers
            if measure != current_measure:
                current_measure = measure
                html_parts.append(f'<div class="measure-header">MEASURE {measure}</div>')
            
            if voice != current_voice and voice:
                current_voice = voice
                html_parts.append(f'<div class="voice-header">VOICE {voice}</div>')
            
            # Format the line
            formatted_line = self._format_diff_line_html(line_type, content, line_number)
            if formatted_line:
                html_parts.append(formatted_line)
                line_number += 1
        
        # Add summary
        summary = self._create_diff_summary(original_lines, transformed_lines)
        html_parts.append(f'<div class="summary">{summary}</div>')
        
        html_parts.append("</div>")
        html_parts.append("</body>")
        html_parts.append("</html>")
        
        return "\n".join(html_parts)
    
    def _create_plain_diff(self, original_tlr: str, transformed_tlr: str) -> str:
        """Create plain text diff without colors"""
        original_lines = original_tlr.splitlines()
        transformed_lines = transformed_tlr.splitlines()
        
        # Create unified diff
        diff = difflib.unified_diff(
            original_lines, 
            transformed_lines,
            fromfile="Original TLR",
            tofile="Transformed TLR",
            lineterm=""
        )
        
        return "\n".join(diff)
    
    def _group_lines_by_structure(self, diff_lines: List[str]) -> List[Tuple[str, str, Optional[int], Optional[str]]]:
        """Group diff lines by measure and voice structure"""
        grouped = []
        current_measure = None
        current_voice = None
        
        for line in diff_lines:
            if line.startswith('  '):
                # Unchanged line
                content = line[2:]
                measure, voice = self._extract_structure_from_line(content)
                grouped.append(('unchanged', content, measure, voice))
            elif line.startswith('- '):
                # Removed line
                content = line[2:]
                measure, voice = self._extract_structure_from_line(content)
                grouped.append(('removed', content, measure, voice))
            elif line.startswith('+ '):
                # Added line
                content = line[2:]
                measure, voice = self._extract_structure_from_line(content)
                grouped.append(('added', content, measure, voice))
            elif line.startswith('? '):
                # Changed line indicator (skip for now, handled by +/-)
                continue
            else:
                # Other diff line (headers, etc.)
                content = line
                measure, voice = None, None
                grouped.append(('other', content, measure, voice))
        
        return grouped
    
    def _extract_structure_from_line(self, line: str) -> Tuple[Optional[int], Optional[str]]:
        """Extract measure and voice numbers from TLR line"""
        measure = None
        voice = None
        
        # Extract measure number
        if line.startswith("MEASURE "):
            try:
                measure = int(line.split()[1])
            except (ValueError, IndexError):
                pass
        
        # Extract voice ID
        if line.startswith("VOICE "):
            try:
                voice = line.split()[1]
            except (ValueError, IndexError):
                pass
        
        return measure, voice
    
    def _format_diff_line_terminal(self, line_type: str, content: str) -> str:
        """Format a single diff line for terminal output"""
        if line_type == 'removed':
            return f"{self.colors['removed']}-{self.colors['reset']} {content}"
        elif line_type == 'added':
            return f"{self.colors['added']}+{self.colors['reset']} {content}"
        elif line_type == 'changed':
            return f"{self.colors['changed']}±{self.colors['reset']} {content}"
        elif line_type == 'unchanged':
            return f"  {content}"
        elif line_type == 'other':
            return f"{self.colors['measure_header']}{content}{self.colors['reset']}"
        else:
            return content
    
    def _format_diff_line_html(self, line_type: str, content: str, line_number: int) -> str:
        """Format a single diff line for HTML output"""
        if line_type == 'removed':
            return f'<div class="line-removed"><span class="line-number">-</span> {content}</div>'
        elif line_type == 'added':
            return f'<div class="line-added"><span class="line-number">+</span> {content}</div>'
        elif line_type == 'changed':
            return f'<div class="line-changed"><span class="line-number">±</span> {content}</div>'
        elif line_type == 'unchanged':
            return f'<div class="line-unchanged"><span class="line-number">{line_number:4d}</span> {content}</div>'
        elif line_type == 'other':
            return f'<div style="font-weight: bold; color: #333;">{content}</div>'
        else:
            return f'<div><span class="line-number">{line_number:4d}</span> {content}</div>'
    
    def _create_diff_summary(self, original_lines: List[str], transformed_lines: List[str]) -> str:
        """Create summary statistics of the diff"""
        original_event_lines = [l for l in original_lines if self._is_event_line(l)]
        transformed_event_lines = [l for l in transformed_lines if self._is_event_line(l)]
        
        added_count = len(transformed_event_lines) - len(original_event_lines)
        removed_count = 0  # Would need more sophisticated analysis
        changed_count = 0  # Would need line-by-line comparison
        
        # Simple change detection
        if len(original_lines) == len(transformed_lines):
            changed_count = sum(1 for o, t in zip(original_lines, transformed_lines) 
                            if o != t and self._is_event_line(o))
        
        summary_parts = []
        if added_count > 0:
            summary_parts.append(f"Added: {added_count} events")
        if removed_count > 0:
            summary_parts.append(f"Removed: {removed_count} events")
        if changed_count > 0:
            summary_parts.append(f"Changed: {changed_count} events")
        
        if not summary_parts:
            return "No changes detected"
        
        return " | ".join(summary_parts)
    
    def _is_event_line(self, line: str) -> bool:
        """Check if line represents a musical event"""
        return (line.startswith("NOTE ") or 
                line.startswith("REST ") or 
                line.startswith("HARMONY ") or 
                line.startswith("LYRIC "))
    
    def create_measure_focused_diff(self, original_tlr: str, transformed_tlr: str, 
                                  target_measure: int, format_type: str = "terminal") -> str:
        """Create diff focused on specific measure"""
        original_lines = original_tlr.splitlines()
        transformed_lines = transformed_tlr.splitlines()
        
        # Filter lines for target measure
        original_measure_lines = self._filter_lines_by_measure(original_lines, target_measure)
        transformed_measure_lines = self._filter_lines_by_measure(transformed_lines, target_measure)
        
        # Create diff for just this measure
        if format_type == "terminal":
            return self._create_terminal_diff("\n".join(original_measure_lines), 
                                           "\n".join(transformed_measure_lines))
        elif format_type == "html":
            return self._create_html_diff("\n".join(original_measure_lines), 
                                        "\n".join(transformed_measure_lines))
        else:
            return self._create_plain_diff("\n".join(original_measure_lines), 
                                       "\n".join(transformed_measure_lines))
    
    def _filter_lines_by_measure(self, lines: List[str], target_measure: int) -> List[str]:
        """Filter lines to only those in target measure and related headers"""
        filtered = []
        in_target_measure = False
        current_measure = None
        
        for line in lines:
            if line.startswith("MEASURE "):
                try:
                    current_measure = int(line.split()[1])
                    in_target_measure = (current_measure == target_measure)
                except (ValueError, IndexError):
                    pass
            
            if in_target_measure or line.startswith("PART ") or line.startswith("VOICE "):
                filtered.append(line)
        
        return filtered