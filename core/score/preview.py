"""
MusicXML Preview Component for Gradio

This module provides interactive preview of MusicXML files directly
in the Gradio interface using music21 for rendering.
"""

import gradio as gr
from pathlib import Path
import tempfile
import base64
from io import BytesIO

MUSIC21_AVAILABLE = False
plt = None
converter = None
stream = None
patches = None

try:
    from music21 import converter, stream
    from music21.musicxml.xmlToM21 import MusicXMLImporter
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    plt = None
    converter = None
    stream = None
    patches = None


def create_score_preview(score_obj):
    """
    Create a visual preview of a Music21 Score.
    
    Args:
        score_obj: music21.stream.Score object
        
    Returns:
        str: Base64 encoded PNG image or error message
    """
    if not MUSIC21_AVAILABLE or plt is None or patches is None:
        return "❌ Music21/Matplotlib not available for preview"
    
    try:
        # Create a simple visualization of the score
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 50)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Simple score representation
        y_offset = 40
        for i, part in enumerate(score_obj.parts[:4]):  # Limit to first 4 parts
            part_name = getattr(part, 'partName', f'Part {i+1}')
            
            # Draw staff line
            ax.plot([10, 90], [y_offset, y_offset], 'k-', linewidth=1)
            
            # Draw part name
            ax.text(2, y_offset + 2, part_name[:10], fontsize=8, ha='left')
            
            # Draw notes (simplified representation)
            for measure in part.getElementsByClass('Measure')[:8]:  # Show first 8 measures
                measure_x = 10 + measure.number * 10
                for note in measure.getElementsByClass(['Note', 'Chord']):
                    note_y = y_offset + note.pitch.midi % 12 * 0.5 - 3
                    ax.add_patch(patches.Circle((measure_x, note_y), 0.3, 
                                           color='blue', zorder=10))
            
            y_offset -= 8
        
        plt.title(f"Score Preview: {len(score_obj.parts)} parts")
        plt.tight_layout()
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        return f"❌ Preview error: {str(e)}"


def create_score_analysis(score_obj):
    """
    Create text analysis of the score.
    
    Args:
        score_obj: music21.stream.Score object
        
    Returns:
        str: Analysis text
    """
    if not MUSIC21_AVAILABLE:
        return "❌ Music21 not available for analysis"
    
    try:
        analysis = []
        analysis.append(f"📄 **Score Analysis**")
        analysis.append(f"")
        
        # Basic info
        analysis.append(f"**Parts:** {len(score_obj.parts)}")
        
        # Measure count
        total_measures = len(score_obj.measureNumbers)
        analysis.append(f"**Measures:** {total_measures}")
        
        # Part details
        analysis.append(f"")
        analysis.append(f"**Voice Details:**")
        for i, part in enumerate(score_obj.parts[:4]):
            part_name = getattr(part, 'partName', f'Voice {i+1}')
            part_measures = len(part.getElementsByClass('Measure'))
            
            # Get pitch range
            notes = [n for n in part.flat.getElementsByClass(['Note', 'Chord']) if hasattr(n, 'pitch')]
            if notes:
                pitches = [note.pitch.midi for note in notes]
                min_pitch = min(pitches)
                max_pitch = max(pitches)
                analysis.append(f"  - **{part_name}**: {part_measures} measures, range {min_pitch}-{max_pitch}")
            else:
                analysis.append(f"  - **{part_name}**: {part_measures} measures (no notes)")
        
        # Time signature info
        if score_obj.parts:
            first_part = score_obj.parts[0]
            time_sigs = first_part.flat.getElementsByClass('TimeSignature')
            if time_sigs:
                time_sig = time_sigs[0]
                analysis.append(f"")
                analysis.append(f"**Time Signature:** {time_sig.numerator}/{time_sig.denominator}")
        
        # Key signature info
        if score_obj.parts:
            first_part = score_obj.parts[0]
            key_sigs = first_part.flat.getElementsByClass('KeySignature')
            if key_sigs:
                key_sig = key_sigs[0]
                analysis.append(f"**Key Signature:** {str(key_sig)}")
        
        return "\n".join(analysis)
        
    except Exception as e:
        return f"❌ Analysis error: {str(e)}"


def preview_musicxml(file_obj):
    """
    Create preview for uploaded MusicXML file.
    
    Args:
        file_obj: Gradio file object
        
    Returns:
        tuple: (image_base64, analysis_text)
    """
    if file_obj is None:
        return None, "Please upload a MusicXML file"
    
    try:
        # Load the score
        if hasattr(file_obj, 'name'):
            file_path = file_obj.name
        else:
            file_path = str(file_obj)
        
        if converter is None:
            return None, "❌ Music21 converter not available"
            
        score_obj = converter.parse(str(file_path))
        
        # Create preview and analysis
        preview_image = create_score_preview(score_obj)
        analysis_text = create_score_analysis(score_obj)
        
        return preview_image, analysis_text
        
    except Exception as e:
        error_msg = f"❌ Error processing MusicXML: {str(e)}"
        return None, error_msg


def create_preview_component():
    """
    Create a Gradio component for MusicXML preview.
    
    Returns:
        gr.Column: Column with preview components
    """
    with gr.Column() as preview_col:
        gr.Markdown("### 📄 MusicXML Preview")
        
        with gr.Row():
            preview_image = gr.Image(
                label="Score Visualization",
                type="pil",
                height=300,
                interactive=False
            )
            
        with gr.Row():
            analysis_text = gr.Textbox(
                label="Score Analysis",
                lines=12,
                max_lines=15,
                interactive=False
            )
    
    return preview_col, preview_image, analysis_text


if __name__ == "__main__":
    # Test the preview functionality
    if not MUSIC21_AVAILABLE:
        print("❌ Music21 not available. Install with: pip install music21")
        exit(1)
    
    # Create test interface
    with gr.Blocks() as demo:
        gr.Markdown("# MusicXML Preview Test")
        
        file_input = gr.File(label="Upload MusicXML", file_types=[".xml", ".musicxml"])
        
        preview_col, preview_image, analysis_text = create_preview_component()
        
        file_input.change(
            fn=preview_musicxml,
            inputs=[file_input],
            outputs=[preview_image, analysis_text]
        )
    
    print("🎵 MusicXML preview component created successfully!")
    print("Run with demo.launch() to test")