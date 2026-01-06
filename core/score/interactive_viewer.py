"""
Interactive MusicXML Score Viewer with Playback Cursor

This module provides an interactive score viewer that can:
- Display MusicXML scores as interactive notation
- Show playback cursor during audio playback
- Allow comparison between input and output scores
- Provide real-time feedback during harmonization
"""

import gradio as gr
import tempfile
import base64
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import threading
import time
from io import BytesIO

try:
    from music21 import converter, stream, note, chord, meter
    from music21 import layout
    from music21 import instrument
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.animation import FuncAnimation
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    plt = None
    converter = None
    stream = None
    patches = None


class InteractiveScoreViewer:
    """Interactive score viewer with playback cursor support."""
    
    def __init__(self):
        self.current_score = None
        self.current_image = None
        self.cursor_position = 0.0  # Time in seconds
        self.is_playing = False
        self.playback_thread = None
        self.measure_positions = []  # List of (measure_start_time, measure_end_time, measure_number)
        
    def load_score(self, score_path: str) -> bool:
        """Load a MusicXML score and prepare for display."""
        if not MUSIC21_AVAILABLE:
            return False
        
        try:
            self.current_score = converter.parse(score_path)
            self._calculate_measure_positions()
            return True
        except Exception as e:
            print(f"Error loading score: {e}")
            return False
    
    def _calculate_measure_positions(self):
        """Calculate start/end times for each measure."""
        if not self.current_score:
            return
        
        self.measure_positions = []
        current_time = 0.0
        
        # Get the first part for timing calculation
        if self.current_score.parts:
            first_part = self.current_score.parts[0]
            
            for measure in first_part.getElementsByClass('Measure'):
                measure_duration = 0.0
                
                # Calculate measure duration from notes
                for element in measure.getElementsByClass(['Note', 'Chord']):
                    if hasattr(element, 'quarterLength'):
                        measure_duration += element.quarterLength
                
                # Store measure position
                measure_end_time = current_time + measure_duration
                self.measure_positions.append({
                    'start': current_time,
                    'end': measure_end_time,
                    'number': measure.number,
                    'duration': measure_duration
                })
                
                current_time = measure_end_time
    
    def render_score_image(self, cursor_time: Optional[float] = None) -> str:
        """
        Render the score as an image with optional playback cursor.
        
        Args:
            cursor_time: Current playback time in seconds
            
        Returns:
            Base64 encoded PNG image
        """
        if not self.current_score or not plt:
            return None
        
        try:
            # Create figure with appropriate size
            fig, ax = plt.subplots(1, 1, figsize=(14, 8))
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 50)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Set font
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
            
            # Draw staff lines for each part
            y_offset = 40
            for i, part in enumerate(self.current_score.parts[:4]):
                part_name = getattr(part, 'partName', f'Part {i+1}')
                
                # Draw staff line
                ax.plot([10, 90], [y_offset, y_offset], 'k-', linewidth=1)
                
                # Draw part name
                ax.text(2, y_offset + 2, part_name[:10], fontsize=8, ha='left')
                
                # Draw measures and notes
                for measure in part.getElementsByClass('Measure')[:8]:
                    measure_x = 10 + measure.number * 10
                    
                    # Draw measure number
                    ax.text(measure_x - 1, y_offset + 4, str(measure.number), 
                           fontsize=6, ha='right', alpha=0.6)
                    
                    # Draw notes
                    for element in measure.getElementsByClass(['Note', 'Chord']):
                        if hasattr(element, 'pitch'):
                            note_y = y_offset + (element.pitch.midi % 12) * 0.3 - 1
                            
                            # Color based on voice
                            voice_colors = ['red', 'blue', 'green', 'orange']
                            color = voice_colors[i % len(voice_colors)]
                            
                            ax.plot(measure_x, note_y, 'o', color=color, markersize=4, zorder=10)
                
                y_offset -= 8
            
            # Draw playback cursor if specified
            if cursor_time is not None:
                self._draw_playback_cursor(ax, cursor_time)
            
            # Add title
            plt.title(f"Interactive Score Viewer - {len(self.current_score.parts)} parts")
            plt.tight_layout()
            
            # Convert to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            print(f"Error rendering score: {e}")
            return None
    
    def _draw_playback_cursor(self, ax, cursor_time: float):
        """Draw a vertical line indicating current playback position."""
        # Find current measure based on time
        current_measure = None
        for measure_pos in self.measure_positions:
            if measure_pos['start'] <= cursor_time <= measure_pos['end']:
                current_measure = measure_pos
                break
        
        if current_measure:
            # Calculate cursor position
            measure_x = 10 + current_measure['number'] * 10
            
            # Draw vertical cursor line
            ax.axvline(x=measure_x, color='red', linewidth=2, alpha=0.8, zorder=20)
            
            # Add cursor label
            ax.text(measure_x, 45, f'▶ {cursor_time:.1f}s', 
                   fontsize=8, color='red', ha='center', zorder=21)
    
    def get_measure_at_time(self, time: float) -> Optional[int]:
        """Get the measure number at a specific time."""
        for measure_pos in self.measure_positions:
            if measure_pos['start'] <= time <= measure_pos['end']:
                return measure_pos['number']
        return None
    
    def get_score_info(self) -> Dict[str, Any]:
        """Get information about the loaded score."""
        if not self.current_score:
            return {}
        
        info = {
            'parts': len(self.current_score.parts),
            'measures': len(self.measure_positions),
            'duration': self.measure_positions[-1]['end'] if self.measure_positions else 0,
            'part_names': []
        }
        
        for part in self.current_score.parts:
            part_name = getattr(part, 'partName', f'Part {len(info["part_names"]) + 1}')
            info['part_names'].append(part_name)
        
        return info


def create_interactive_viewer() -> Tuple[gr.Column, gr.Image, gr.Textbox, gr.Slider]:
    """
    Create an interactive score viewer component for Gradio.
    
    Returns:
        Tuple of (column, image_component, info_text, cursor_slider)
    """
    viewer = InteractiveScoreViewer()
    
    with gr.Column() as viewer_col:
        gr.Markdown("### 🎼 Interactive Score Viewer")
        
        with gr.Row():
            score_image = gr.Image(
                label="Score Notation",
                type="filepath",
                height=300,
                interactive=False
            )
        
        with gr.Row():
            with gr.Column(scale=3):
                cursor_slider = gr.Slider(
                    minimum=0,
                    maximum=30,
                    value=0,
                    step=0.1,
                    label="🎵 Playback Cursor (seconds)",
                    interactive=True
                )
            with gr.Column(scale=1):
                update_btn = gr.Button("🔄 Update View", size="sm")
        
        with gr.Row():
            score_info = gr.Textbox(
                label="📊 Score Information",
                lines=4,
                max_lines=6,
                interactive=False
            )
    
    # Store viewer instance in component for access
    viewer_col.viewer_instance = viewer
    
    return viewer_col, score_image, score_info, cursor_slider


def update_score_view(file_obj, cursor_time: float = 0.0) -> Tuple[str, str]:
    """
    Update the score view with new file and cursor position.
    
    Args:
        file_obj: Uploaded MusicXML file
        cursor_time: Current cursor position in seconds
        
    Returns:
        Tuple of (image_path, info_text)
    """
    if file_obj is None:
        return None, "Please upload a MusicXML file"
    
    # Get viewer from component (this is a bit hacky but works)
    viewer = InteractiveScoreViewer()
    
    try:
        # Load score
        if hasattr(file_obj, 'name'):
            file_path = file_obj.name
        else:
            file_path = str(file_obj)
        
        if not viewer.load_score(file_path):
            return None, "❌ Failed to load MusicXML file"
        
        # Render with cursor
        image_data = viewer.render_score_image(cursor_time)
        
        # Get score info
        info = viewer.get_score_info()
        info_text = f"""📄 **Score Information**
Parts: {info.get('parts', 0)}
Measures: {info.get('measures', 0)}
Duration: {info.get('duration', 0):.1f} seconds
Part Names: {', '.join(info.get('part_names', []))}"""
        
        return image_data, info_text
        
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


def create_comparison_viewer() -> gr.Column:
    """
    Create a side-by-side comparison viewer for input vs output scores.
    
    Returns:
        Gradio Column with comparison components
    """
    with gr.Column() as comp_col:
        gr.Markdown("### 🔄 Input vs Output Comparison")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### 📥 Input Score")
                input_image = gr.Image(
                    label="Original Score",
                    type="filepath",
                    height=250,
                    interactive=False
                )
                input_info = gr.Textbox(
                    label="Input Info",
                    lines=3,
                    max_lines=4,
                    interactive=False
                )
            
            with gr.Column():
                gr.Markdown("#### 📤 Output Score")
                output_image = gr.Image(
                    label="Harmonized Score",
                    type="filepath",
                    height=250,
                    interactive=False
                )
                output_info = gr.Textbox(
                    label="Output Info",
                    lines=3,
                    max_lines=4,
                    interactive=False
                )
        
        with gr.Row():
            comparison_btn = gr.Button("🔄 Update Comparison", size="sm")
    
    return comp_col


def update_comparison(input_file, output_file) -> Tuple[str, str, str, str]:
    """
    Update the comparison view with input and output scores.
    
    Args:
        input_file: Original MusicXML file
        output_file: Harmonized MusicXML file
        
    Returns:
        Tuple of (input_image, input_info, output_image, output_info)
    """
    # Load input score
    input_viewer = InteractiveScoreViewer()
    input_image = None
    input_info = "No input file"
    
    if input_file:
        try:
            if hasattr(input_file, 'name'):
                input_path = input_file.name
            else:
                input_path = str(input_file)
            
            if input_viewer.load_score(input_path):
                input_image = input_viewer.render_score_image()
                input_info_dict = input_viewer.get_score_info()
                input_info = f"Parts: {input_info_dict.get('parts', 0)}\nMeasures: {input_info_dict.get('measures', 0)}"
        except Exception as e:
            input_info = f"❌ Input error: {e}"
    
    # Load output score
    output_viewer = InteractiveScoreViewer()
    output_image = None
    output_info = "No output file"
    
    if output_file:
        try:
            if hasattr(output_file, 'name'):
                output_path = output_file.name
            else:
                output_path = str(output_file)
            
            if output_viewer.load_score(output_path):
                output_image = output_viewer.render_score_image()
                output_info_dict = output_viewer.get_score_info()
                output_info = f"Parts: {output_info_dict.get('parts', 0)}\nMeasures: {output_info_dict.get('measures', 0)}"
        except Exception as e:
            output_info = f"❌ Output error: {e}"
    
    return input_image, input_info, output_image, output_info


if __name__ == "__main__":
    # Test the interactive viewer
    if not MUSIC21_AVAILABLE:
        print("❌ Music21 not available. Install with: pip install music21")
        exit(1)
    
    # Create test interface
    with gr.Blocks() as demo:
        gr.Markdown("# 🎼 Interactive MusicXML Score Viewer")
        
        file_input = gr.File(label="Upload MusicXML", file_types=[".xml", ".musicxml"])
        
        viewer_col, score_image, score_info, cursor_slider = create_interactive_viewer()
        
        file_input.change(
            fn=update_score_view,
            inputs=[file_input, cursor_slider],
            outputs=[score_image, score_info]
        )
        
        cursor_slider.change(
            fn=lambda t: update_score_view(file_input.value, t),
            inputs=[cursor_slider],
            outputs=[score_image, score_info]
        )
    
    print("🎼 Interactive score viewer created successfully!")
    print("Features:")
    print("  - Interactive score notation display")
    print("  - Playback cursor with time tracking")
    print("  - Measure position calculation")
    print("  - Side-by-side comparison support")
    print("Run with demo.launch() to test")