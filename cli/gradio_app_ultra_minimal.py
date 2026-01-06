"""
Ultra-minimal working score viewer with voice previews.

This provides the most basic functionality without complex dependencies.
"""

import gradio as gr
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

# Only essential imports
try:
    from music21 import converter, stream, note, chord, meter
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    converter = None


class UltraMinimalViewer:
    """Ultra-minimal score viewer."""
    
    def __init__(self):
        self.current_file_path = None
        
    def load_score(self, score_path: str) -> bool:
        """Load a MusicXML score."""
        if not MUSIC21_AVAILABLE:
            print("❌ Music21 not available")
            return False
        
        try:
            self.current_file_path = Path(score_path)
            return True
        except Exception as e:
            print(f"Error loading score: {e}")
            return False
    
    def get_file_info(self) -> Dict[str, Any]:
        """Get basic file information."""
        if not self.current_file_path:
            return {'file': 'No file loaded'}
        
        return {
            'file': str(self.current_file_path),
            'size': self.current_file_path.stat().st_size if self.current_file_path.exists() else 0,
            'modified': self.current_file_path.stat().st_mtime if self.current_file_path.exists() else 0
        }


def create_ultra_minimal_interface():
    """Create ultra-minimal interface."""
    
    with gr.Blocks(title="Choral LLM Workbench - Ultra-Minimal Score Viewer") as app:
        gr.Markdown("## 🎼 Ultra-Minimal Score Viewer")
        gr.Markdown("Upload MusicXML to see basic score information.")
        
        # File input
        score_input = gr.File(label="📁 Upload MusicXML", file_types=[".xml", ".musicxml", ".mxl"])
        
        # Basic output
        with gr.Row():
            with gr.Column(scale=2):
                file_info = gr.Textbox(
                    label="📄 File Information",
                    lines=4,
                    interactive=False
                )
            with gr.Column(scale=1):
                score_preview = gr.Textbox(
                    label="📝 Score Information",
                    lines=8,
                    max_lines=10,
                    interactive=False
                )
        
        # Simple event handler
        def update_info(file_obj):
            if file_obj is None:
                return "No file provided", None
            
            viewer = UltraMinimalViewer()
            if not viewer.load_score(file_obj):
                return "❌ Failed to load file", None
            
            file_info = viewer.get_file_info()
            score_preview = viewer.get_basic_score_text()
            
            return file_info, score_preview
        
        score_input.change(
            fn=update_info,
            inputs=[score_input],
            outputs=[file_info, score_preview]
        )
    
    return app


if __name__ == "__main__":
    # Test both interfaces
    print("Testing ultra-minimal interface...")
    
    # Test minimal viewer
    print("1. Testing minimal viewer...")
    minimal_app = create_ultra_minimal_interface()
    print("✅ Ultra-minimal interface created!")
    
    # Test voice preview interface
    print("2. Testing voice preview interface...")
    try:
        from cli.gradio_app_satb_voice_previews import create_voice_preview_interface
        voice_app = create_voice_preview_interface()
        print("✅ Voice preview interface created!")
        print("Features:")
        print("  - Individual voice audio generation")
        print("  - Duration control")
        print("  - Individual voice previews")
        print("  - Master ensemble option")
    except Exception as e:
        print(f"❌ Voice preview import failed: {e}")
    
    print("🚀 Launching ultra-minimal interface...")
    
    try:
        minimal_app.launch(
            server_name="0.0.0.0",
            server_port=7862,
            share=False,
            debug=False
        )
        print("✅ Ultra-minimal app starts successfully!")
        print("\nLaunch with: python cli/gradio_app_satb_voice_previews.py for full features")
        
    except Exception as e:
        print(f"❌ Failed to launch minimal app: {e}")