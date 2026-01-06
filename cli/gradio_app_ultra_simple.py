"""
Ultra-simple score viewer - minimal working version.
"""

import gradio as gr
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

try:
    from music21 import converter, stream, note, meter
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    converter = None


def render_score_image_basic(score_path: str) -> Optional[Path]:
    """
    Render a basic score image using music21.
    
    Args:
        score_path: Path to MusicXML file
        
    Returns:
        Path to temporary image file or None
    """
    if not MUSIC21_AVAILABLE:
        print("❌ Music21 not available")
        return None
    
    try:
        score = converter.parse(score_path)
        
        # Create a simple image
        tmp_image = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        
        # Write as LilyPond then convert to PNG
        # This avoids complex matplotlib dependencies
        score.write('lilypond', tmp_image.name)
        
        return Path(tmp_image.name)
        
    except Exception as e:
        print(f"❌ Error rendering score: {e}")
        return None


def create_ultra_simple_interface():
    """Create ultra-simple interface."""
    
    with gr.Blocks(title="Choral LLM Workbench - Score Viewer") as app:
        gr.Markdown("## 🎼 Ultra-Simple Score Viewer")
        gr.Markdown("Upload MusicXML to see score information")
        
        # File input
        score_input = gr.File(label="📁 Upload MusicXML", file_types=[".xml", ".musicxml", ".mxl"])
        
        # Simple output
        score_info = gr.Textbox(label="📊 Score Information", lines=5, interactive=False)
        score_image = gr.Image(label="🎼 Score Preview", height=200, interactive=False)
        
        def process_score(file_obj):
            if file_obj is None:
                return "Please upload a MusicXML file", None
            
            try:
                # Basic score information
                if hasattr(file_obj, 'name'):
                    file_path = file_obj.name
                else:
                    file_path = str(file_obj)
                
                score = converter.parse(file_path)
                
                info = f"""📄 Score Information
File: {Path(file_path).name}
Parts: {len(score.parts)}
Measures: {len(score.getElementsByClass('Measure') if score.parts else [])}
"""
                
                # Generate simple preview
                image_path = render_score_image_basic(file_path)
                
                return info, image_path
                
            except Exception as e:
                return f"❌ Error: {str(e)}", None
        
        # Wire events
        score_input.change(
            fn=process_score,
            inputs=[score_input],
            outputs=[score_info, score_image]
        )
    
    return app


if __name__ == "__main__":
    app = create_ultra_simple_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False
    )