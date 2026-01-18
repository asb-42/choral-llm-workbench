from dataclasses import dataclass
from typing import List, Optional
from semantic_diff_analyzer import SemanticDiffEntry


class SemanticDiffUI:
    """UI renderer for semantic diffs - converts SemanticDiffEntry to HTML"""

    def __init__(self):
        self.css_styles = """
        <style>
        .diff-rhythm { color: #6bbcff; }
        .diff-pitch { color: #7dff7d; }
        .diff-harmony { color: #c792ea; }
        .diff-style { color: #ffb86c; }
        .diff-struct { color: #cccccc; }

        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            .diff-rhythm { color: #4a9eff; }
            .diff-pitch { color: #5cb85c; }
            .diff-harmony { color: #a8757a; }
            .diff-style { color: #e6a55a; }
            .diff-struct { color: #666666; }
        }

        .semantic-diff-container {
            max-height: 400px;
            overflow-y: auto;
            padding: 10px;
            background-color: transparent;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.4;
        }

        .diff-group-header {
            font-weight: bold;
            margin-top: 15px;
            margin-bottom: 8px;
            color: #333;
        }

        .diff-entry {
            margin-bottom: 6px;
            padding-left: 10px;
        }
        </style>
        """

    def render_semantic_diff_html(self, entries: List[SemanticDiffEntry]) -> str:
        """
        Render semantic diff entries as HTML with colors and grouping

        Args:
            entries: List of SemanticDiffEntry objects

        Returns:
            HTML string with CSS styles and semantic diff display
        """
        if not entries:
            return self.css_styles + """
            <div class="semantic-diff-container">
                <p style="color: #666;">No semantic diff available. Transform music first.</p>
            </div>
            """

        # Group entries by scope
        grouped_entries = self._group_entries_by_scope(entries)

        html_parts = [self.css_styles, '<div class="semantic-diff-container">']

        for scope, scope_entries in grouped_entries.items():
            scope_icon = self._get_scope_icon(scope)
            scope_title = self._get_scope_title(scope)

            html_parts.append(f'<div class="diff-group-header">{scope_icon} {scope_title}</div>')

            for entry in scope_entries:
                change_icon = self._get_change_icon(entry.change_type)
                css_class = self._get_css_class(entry.change_type)

                location_text = f" {entry.location}" if entry.location else ""
                description = entry.description

                html_parts.append(
                    f'<div class="diff-entry">'
                    f'<span class="{css_class}">'
                    f'{change_icon} {entry.location}: {description}'
                    f'</span></div>'
                )

        html_parts.append('</div>')
        return ''.join(html_parts)

    def _group_entries_by_scope(self, entries: List[SemanticDiffEntry]) -> dict:
        """Group entries by scope for organized display"""
        groups = {}
        for entry in entries:
            scope = entry.scope
            if scope not in groups:
                groups[scope] = []
            groups[scope].append(entry)
        return groups

    def _get_scope_icon(self, scope: str) -> str:
        """Get icon for scope type"""
        icons = {
            "score": "🎼",
            "part": "📋",
            "voice": "🎤",
            "measure": "📍",
            "note": "🎵",
            "harmony": "🎼",
            "rhythm": "⏱️"
        }
        return icons.get(scope, "📝")

    def _get_scope_title(self, scope: str) -> str:
        """Get human-readable title for scope"""
        titles = {
            "score": "Score Changes",
            "part": "Part Changes",
            "voice": "Voice Changes",
            "measure": "Measure Changes",
            "note": "Note Changes",
            "harmony": "Harmony Changes",
            "rhythm": "Rhythm Changes"
        }
        return titles.get(scope, f"{scope.title()} Changes")

    def _get_change_icon(self, change_type: str) -> str:
        """Get icon for change type"""
        icons = {
            "rhythm": "⏱️",
            "pitch": "🔊",
            "harmony": "🎼",
            "style": "🎭",
            "structure": "🏗️"
        }
        return icons.get(change_type, "📝")

    def _get_css_class(self, change_type: str) -> str:
        """Get CSS class for change type"""
        class_map = {
            "rhythm": "diff-rhythm",
            "pitch": "diff-pitch",
            "harmony": "diff-harmony",
            "style": "diff-style",
            "structure": "diff-struct"
        }
        return class_map.get(change_type, "diff-struct")