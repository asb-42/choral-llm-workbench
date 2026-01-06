"""
Simple but functional score viewer without complex dependencies.
"""

import gradio as gr
import tempfile
import base64
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

try:
    from music21 import converter, stream, note, meter
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
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


class SimpleScoreViewer:
    """Simplified score viewer without complex dependencies."""
    
    def __init__(self):
        self.current_score = None
        self.score_info = {}
        
    def load_score(self, score_path: str) -> bool:
        """Load a MusicXML score."""
        if not MUSIC21_AVAILABLE:
            return False
        
        try:
            self.current_score = converter.parse(score_path)
            self._extract_score_info()
            return True
        except Exception as e:
            print(f"Error loading score: {e}")
            return False
    
    def _extract_score_info(self):
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
            first_part = self.current_score.parts[0]
            self.score_info['measures'] = len(first_part.getElementsByClass('Measure'))
            
            for part in self.current_score.parts:
                part_name = getattr(part, 'partName', f'Part {len(self.score_info["part_names"]) + 1}')
                self.score_info['part_names'].append(part_name)
    
    def render_score_image(self) -> Optional[str]:
        """Render a simplified score image."""
        if not self.current_score or not plt:
            return None
        
        try:
            # Create simple figure
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 30)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Simple score representation
            y_offset = 25
            for i, part in enumerate(self.current_score.parts[:4]):
                part_num = i + 1
                
                # Draw staff line
                ax.plot([10, 90], [y_offset, y_offset], 'k-', linewidth=1)
                
                # Draw part number
                ax.text(2, y_offset + 1, f'Voice {part_num}', fontsize=8, ha='left')
                
                # Draw first few notes (simplified)
                note_count = 0
                for measure in part.getElementsByClass('Measure')[:6]:  # Show first 6 measures
                    if note_count >= 12:  # Limit total notes
                        break
                    measure_x = 10 + measure.number * 12
                    
                    for element in measure.getElementsByClass(['Note', 'Chord']):
                        if note_count >= 12:
                            break
                        if hasattr(element, 'pitch'):
                            # Simple circle for each note
                            ax.plot(measure_x, y_offset + (element.pitch.midi % 12) * 0.4 - 2, 
                                   'o', markersize=2, zorder=10)
                            note_count += 1
                
                y_offset -= 6
            
            # Simple title
            plt.title(f"Score Viewer - {self.score_info['parts']} parts, {self.score_info['measures']} measures")
            plt.tight_layout()
            
            # Save to file and return file path
            tmp_image = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            plt.savefig(tmp_image.name, format='png', dpi=80, bbox_inches='tight')
            plt.close()
            return tmp_image.name
            
        except Exception as e:
            print(f"Error rendering image: {e}")
            return None
    
    def get_score_info(self) -> Dict[str, Any]:
        """Get score information."""
        return self.score_info


def create_simple_viewer() -> Tuple[gr.Column, gr.Image, gr.Textbox]:
    """Create a simple but functional score viewer."""
    viewer = SimpleScoreViewer()
    
    with gr.Column() as viewer_col:
        gr.Markdown("### 🎼 Simple Score Viewer")
        
        with gr.Row():
            score_image = gr.Image(
                label="Score Visualization",
                height=200,
                interactive=False
            )
        
        with gr.Row():
            score_info = gr.Textbox(
                label="Score Information",
                lines=4,
                max_lines=6,
                interactive=False
            )
    
    # Store viewer instance for access
    viewer_col.viewer_instance = viewer
    
    return viewer_col, score_image, score_info


def update_simple_view(file_obj) -> Tuple[str, str]:
    """Update the simple score view."""
    if file_obj is None:
        return None, "Please upload a MusicXML file"
    
    # Get viewer from component
    viewer = SimpleScoreViewer()
    
    try:
        # Load score
        if hasattr(file_obj, 'name'):
            file_path = file_obj.name
        else:
            file_path = str(file_obj)
        
        if not viewer.load_score(file_path):
            return None, "❌ Failed to load MusicXML file"
        
        # Render image
        image_data = viewer.render_score_image()
        
        # Get score info
        info_dict = viewer.get_score_info()
        info_text = f"""📄 **Score Information**
Parts: {info_dict.get('parts', 0)}
Measures: {info_dict.get('measures', 0)}
Part Names: {', '.join(info_dict.get('part_names', []))}"""
        
        return image_data, info_text
        
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


def create_enhanced_interface():
    """Create enhanced interface with simple score viewer."""
    
    with gr.Blocks(title="Choral LLM Workbench - Simple Score Viewer") as app:
        gr.Markdown("## 🎼 SATB Harmonization with Score Viewer")
        gr.Markdown("Upload MusicXML and see the score notation!")
        
        # File input section
        with gr.Row():
            score_input = gr.File(label="📁 Upload MusicXML", file_types=[".xml", ".musicxml", ".mxl"])
        
        # Score viewer section
        viewer_col, score_image, score_info = create_simple_viewer()
        
        # Audio tuning controls
        with gr.Row():
            with gr.Column(scale=2):
                tuning_slider = gr.Slider(
                    minimum=432.0,
                    maximum=443.0,
                    value=432.0,
                    step=1.0,
                    label="🎛️ Base Tuning (Hz)"
                )
            with gr.Column(scale=1):
                tuning_display = gr.Textbox(
                    label="Current Tuning",
                    value="432.0 Hz",
                    interactive=False
                )
        
        # Voice prompts section
        gr.Markdown("### 🎤 Voice-Specific Prompts")
        with gr.Row():
            s_prompt = gr.Textbox(label="🎼 Soprano", value="Make soprano more lyrical")
            a_prompt = gr.Textbox(label="🎼 Alto", value="Add rich harmonies to alto")
        with gr.Row():
            t_prompt = gr.Textbox(label="🎼 Tenor", value="Enhance tenor with warm tones")
            b_prompt = gr.Textbox(label="🎼 Bass", value="Create solid harmonic foundation")
        
        # Action buttons
        with gr.Row():
            harmonize_btn = gr.Button("🎯 Harmonize Score", variant="primary", size="lg")
        
        # Output section
        gr.Markdown("### 📤 Output Results")
        with gr.Row():
            with gr.Column():
                output_file = gr.File(label="📄 Harmonized MusicXML", interactive=False)
            with gr.Column():
                output_audio = gr.Audio(label="🎵 Audio Preview", interactive=False)
        
        with gr.Row():
            output_summary = gr.Textbox(
                label="📝 Summary",
                lines=8,
                max_lines=12,
                interactive=False
            )
        
        # Event handlers
        def update_prompts(s_prompt, a_prompt, t_prompt, b_prompt):
            return {"S": s_prompt, "A": a_prompt, "T": t_prompt, "B": b_prompt}
        
        def update_tuning_display(tuning_value):
            return f"{tuning_value} Hz"
        
        def simple_harmonize(score_file, prompts, base_tuning):
            """Simple harmonization without complex dependencies."""
            if score_file is None:
                return None, None, "Please upload a MusicXML file"
            
            try:
                from core.score import load_musicxml, write_musicxml
                from core.editor.dummy_llm import DummyLLM
                from core.score.reharmonize import replace_chord_in_measure
                from core.audio import score_to_midi, render_score_audio
                
                # Load score
                score = load_musicxml(score_file)
                
                # Simple LLM suggestions
                llm = DummyLLM()
                llm_suggestions = llm.harmonize_multi_voice(prompts)
                
                # Apply suggestions to first few measures
                for voice, suggestion in llm_suggestions.items():
                    measure_num = suggestion.get('measure', 1)
                    if measure_num <= 4:  # Only modify first 4 measures
                        new_root = suggestion.get('root', 'C')
                        try:
                            replace_chord_in_measure(score, measure_num, new_root, 'major')
                        except Exception as e:
                            print(f"Could not replace chord in measure {measure_num}: {e}")

                # Save updated MusicXML
                tmp_xml = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
                write_musicxml(score, tmp_xml.name)
                
                # Generate audio preview
                try:
                    midi_path = score_to_midi(score)
                    wav_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                    wav_path = Path(wav_tmp.name)
                    
                    # Render with 30 second limit
                    from core.audio import render_audio_with_tuning
                    render_audio_with_tuning(
                        midi_path=str(midi_path),
                        wav_path=str(wav_path),
                        base_tuning=base_tuning,
                        duration_limit=30
                    )
                    audio_path = str(wav_path)
                    midi_path.unlink()
                    
                except Exception as audio_error:
                    print(f"Audio rendering failed: {audio_error}")
                    audio_path = None
                
                # Create summary
                summary = f"""✅ **Harmonization Complete**

**Applied Changes:**
- Voice prompts processed for S/A/T/B
- Chord replacements in measures 1-4
- Base tuning: {base_tuning} Hz
- Audio duration: Limited to 30 seconds

**Output Files:**
- MusicXML: Ready for download
- Audio: {'Available' if audio_path else 'Not available'}

**Summary:**
Score harmonized with {len(llm_suggestions)} voice suggestions.
Duration limited to prevent overly long audio files.
Simple score viewer shows basic notation.
"""
                
                return str(Path(tmp_xml.name)), audio_path, summary
                
            except Exception as e:
                return None, None, f"❌ **Error:** {str(e)}"
        
        # State management
        prompts_state = gr.State({})
        
        # Wire up events
        for prompt_input in [s_prompt, a_prompt, t_prompt, b_prompt]:
            prompt_input.change(
                fn=update_prompts,
                inputs=[s_prompt, a_prompt, t_prompt, b_prompt],
                outputs=[prompts_state]
            )
        
        tuning_slider.change(
            fn=update_tuning_display,
            inputs=[tuning_slider],
            outputs=[tuning_display]
        )
        
        score_input.change(
            fn=update_simple_view,
            inputs=[score_input],
            outputs=[score_image, score_info]
        )
        
        harmonize_btn.click(
            fn=simple_harmonize,
            inputs=[score_input, prompts_state, tuning_slider],
            outputs=[output_file, output_audio, output_summary]
        )
    
    return app


if __name__ == "__main__":
    app = create_enhanced_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False
    )