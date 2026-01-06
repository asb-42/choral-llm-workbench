"""
Working score viewer with basic functionality.
"""

import gradio as gr
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from music21 import converter, stream, note, chord, meter
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    converter = None


def create_basic_viewer() -> tuple:
    """Create a basic but functional score viewer."""
    
    viewer = BasicScoreViewer()
    
    with gr.Column() as viewer_col:
        gr.Markdown("### 🎼 Basic Score Viewer")
        
        with gr.Row():
            score_input = gr.File(
                label="📁 Upload MusicXML", 
                file_types=[".xml", ".musicxml", ".mxl"]
            )
            with gr.Column(scale=1):
                score_info = gr.Textbox(
                    label="📊 Score Information",
                    lines=6,
                    max_lines=8,
                    interactive=False
                )
        
        with gr.Row():
            score_image = gr.Image(
                label="📄 Score Visualization",
                height=300,
                interactive=False
            )
    
        # Event handler
        def update_view(file_obj):
            return viewer.update_score_view(file_obj)
        
        # Wire up event
        score_input.change(
            fn=update_view,
            inputs=[score_input],
            outputs=[score_info, score_image]
        )
    
    return viewer_col, score_input, score_info, score_image


class BasicScoreViewer:
    """Basic score viewer with minimal dependencies."""
    
    def __init__(self):
        self.current_score = None
        self.score_info = {}
        
    def update_score_view(self, file_obj) -> tuple:
        """Update the score view with new file."""
        if file_obj is None:
            return None, "Please upload a MusicXML file"
        
        try:
            if hasattr(file_obj, 'name'):
                file_path = file_obj.name
            else:
                file_path = str(file_obj)
            
            self.current_score = converter.parse(file_path)
            self._extract_basic_info()
            return True, self.get_score_info_text()
            
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
    
    def _extract_basic_info(self):
        """Extract basic information from score."""
        if not self.current_score:
            return
        
        self.score_info = {
            'parts': len(self.current_score.parts),
            'measures': 0,
            'part_names': []
        }
        
        # Count measures and get part names
        if self.current_score.parts:
            self.score_info['measures'] = len(self.current_score.parts[0].getElementsByClass('Measure'))
            
            for part in self.current_score.parts:
                part_name = getattr(part, 'partName', f'Part {len(self.score_info.get("part_names", [])) + 1}')
                self.score_info['part_names'].append(part_name)
    
    def get_score_info_text(self) -> str:
        """Get score information as text."""
        if not self.score_info:
            return "No score loaded"
        
        return f"""📊 **Score Information**
Parts: {self.score_info.get('parts', 0)}
Measures: {self.score_info.get('measures', 0)}
Part Names: {', '.join(self.score_info.get('part_names', []))}
"""
    
    def render_score_preview(self) -> Optional[str]:
        """Render a basic score preview."""
        if not self.current_score:
            return None
        
        try:
            # Create simple figure
            fig, ax = plt.subplots(1, 1, figsize=(12, 8))
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 50)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Basic score representation
            y_offset = 25
            for i, part in enumerate(self.current_score.parts[:4]):
                part_num = i + 1
                
                # Draw staff line
                ax.plot([10, 90], [y_offset, y_offset], 'k-', linewidth=1)
                
                # Draw part name
                ax.text(2, y_offset + 2, f'Voice {part_num}', fontsize=8, ha='left')
                
                # Draw first few notes (simplified)
                note_count = 0
                for measure in part.getElementsByClass('Measure')[:6]:  # Show first 6 measures
                    if note_count >= 8:  # Limit total notes
                        break
                    measure_x = 10 + measure.number * 12
                    
                    for element in measure.getElementsByClass(['Note', 'Chord']):
                        if note_count >= 8:
                            break
                        if hasattr(element, 'pitch'):
                            note_y = y_offset + (element.pitch.midi % 12) * 0.3 - 1
                            # Simple circle for each note
                            ax.plot(measure_x, note_y, 'o', markersize=3, zorder=10)
                            note_count += 1
                
                y_offset -= 6
            
            # Simple title
            plt.title(f"Score Viewer - {self.score_info.get('parts', 0)} parts")
            plt.tight_layout()
            
            # Convert to base64
            buffer = plt.BytesIO()
            plt.savefig(buffer, format='png', dpi=80, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            print(f"Error rendering preview: {e}")
            return None


def create_voice_preview_interface():
    """Create the voice preview interface."""
    
    with gr.Blocks(title="Choral LLM Workbench - Voice Previews") as app:
        gr.Markdown("## 🎼 SATB Voice Preview Interface")
        gr.Markdown("Upload MusicXML to preview individual voices and generate audio.")
        
        # File input
        score_input = gr.File(label="📁 Upload MusicXML", file_types=[".xml", ".musicxml", ".mxl"])
        
        # Display areas
        with gr.Row():
            with gr.Column(scale=1):
                score_info = gr.Textbox(
                    label="📊 Score Information",
                    lines=6,
                    interactive=False
                )
                score_preview = gr.Image(
                    label="📝 Score Preview",
                    height=300
                )
            
            with gr.Column(scale=2):
                # Voice controls
                with gr.Row():
                    with gr.Column():
                        soprano_check = gr.Checkbox(label="🎵 Soprano", value=True)
                        alto_check = gr.Checkbox(label="🎵 Alto", value=True)
                    with gr.Column():
                        tenor_check = gr.Checkbox(label="🎵 Tenor", value=True)
                        bass_check = gr.Checkbox(label="🎵 Bass", value=True)
                
                # Duration control
                duration = gr.Slider(
                    minimum=5,
                    maximum=60,
                    value=15,
                    step=5,
                    label="⏱️ Duration (seconds)"
                )
                
                # Audio outputs
                with gr.Row():
                    soprano_audio = gr.Audio(label="Soprano")
                    alto_audio = gr.Audio(label="Alto")
                with gr.Row():
                    tenor_audio = gr.Audio(label="Tenor")
                    bass_audio = gr.Audio(label="Bass")
                
                # Master audio
                master_audio = gr.Audio(label="🎼 Full Ensemble")
        
        # Event handlers
        viewer = BasicScoreViewer()
        
        def update_interface(file_obj):
            """Update all interface elements."""
            if file_obj is None:
                return (
                    "No file uploaded",
                    None,
                    *[None] * 6  # 6 audio outputs
                )
            
            try:
                success, preview = viewer.update_score_view(file_obj)
                info_text = viewer.get_score_info_text()
                
                return (
                    info_text,
                    preview,
                    *[None] * 6  # Audio will be generated on demand
                )
            except Exception as e:
                return (
                    f"❌ Error: {str(e)}",
                    None,
                    *[None] * 6
                )
        
        score_input.change(
            fn=update_interface,
            inputs=[score_input],
            outputs=[
                score_info, score_preview,
                soprano_audio, alto_audio, tenor_audio, bass_audio, master_audio
            ]
        )
    
    return app