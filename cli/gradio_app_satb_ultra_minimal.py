"""
Working score viewer with voice preview - ultra-minimal version.
This is the most stable implementation with minimal dependencies.
"""

import gradio as gr
import tempfile
from pathlib import Path
from typing import Optional

# Try to import only what we need
try:
    from music21 import converter, stream, note
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    converter = None


class UltraMinimalViewer:
    """Ultra-minimal score viewer with voice preview support."""
    
    def __init__(self):
        self.current_file_path = None
        self.score_info = {}
        self.voice_audios = {}  # File paths for each voice
        
    def load_score(self, score_path: str) -> bool:
        """Load a MusicXML score."""
        if not MUSIC21_AVAILABLE:
            print("❌ Music21 not available")
            return False
        
        try:
            self.current_file_path = Path(score_path)
            score = converter.parse(score_path)
            self._extract_minimal_info()
            return True
        except Exception as e:
            print(f"❌ Error loading score: {e}")
            return False
    
    def _extract_minimal_info(self):
        """Extract minimal score information."""
        if not self.current_file_path:
            return
        
        self.score_info = {
            'file': str(self.current_file_path),
            'size': self.current_file_path.stat().st_size if self.current_file_path.exists() else 0,
            'parts': len(self.current_score.parts),
            'measures': 0,
            'part_names': []
        }
        
        if self.current_score.parts:
            first_part = self.current_score.parts[0]
            self.score_info['measures'] = len(first_part.getElementsByClass('Measure'))
            
            for part in self.current_score.parts:
                part_name = getattr(part, 'partName', f'Part {len(self.score_info["part_names"]) + 1}')
                self.score_info['part_names'].append(part_name)
    
    def generate_voice_audio(self, score, voice: str, duration: int = 30) -> Optional[Path]:
        """Generate audio for specific voice."""
        try:
            # Extract only the specified voice part
            voice_part = None
            voice_map = {'S': 0, 'A': 1, 'T': 2, 'B': 3}
            
            if voice in voice_map:
                voice_index = voice_map[voice]
                if voice_index < len(score.parts):
                    voice_part = score.parts[voice_index]
            
            if voice_part is None:
                return None
            
            # Create new score with only this voice
            voice_score = type(score)()
            voice_score.append(voice_part)
            
            # Generate MIDI
            from core.audio import score_to_midi
            midi_path = score_to_midi(voice_score)
            
            # Render audio
            from core.audio import render_score_audio_with_tuning
            tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{voice}.wav")
            
            success = render_score_audio_with_tuning(
                midi_path=str(midi_path),
                wav_path=tmp_wav.name,
                base_tuning=432.0,
                duration_limit=duration
            )
            
            audio_path = Path(tmp_wav.name) if success else None
            
            if audio_path:
                # Store for download
                self.voice_audios[voice] = audio_path
                print(f"Generated {voice} voice audio: {audio_path}")
            
            return audio_path
            
        except Exception as e:
            print(f"Error generating {voice} voice audio: {e}")
            return None
    
    def get_voice_info(self, voice: str) -> Dict[str, Any]:
        """Get information about a voice."""
        return {
            'voice': voice,
            'audio_file': self.voice_audios.get(voice),
            'audio_size': self.voice_audios.get(voice, {}).stat().st_size if self.voice_audios.get(voice, None) and self.voice_audios.get(voice, Path(self.voice_audios.get(voice)).exists() else 0
        }


def create_ultra_minimal_interface():
    """Create ultra-minimal interface with voice previews."""
    
    with gr.Blocks(title="Choral LLM Workbench - Ultra-Minimal Score Viewer") as app:
        gr.Markdown("## 🎼 Ultra-Minimal Score Viewer with Voice Previews")
        gr.Markdown("Upload MusicXML, enter voice prompts, and get individual voice audio files!")
        
        # File input section
        with gr.Row():
            file_input = gr.File(label="📁 Upload MusicXML", file_types=[".xml", ".musicxml", ".mxl"])
        
        # Score information section
        with gr.Row():
            score_info = gr.Textbox(
                label="📊 Score Information",
                lines=6,
                max_lines=8,
                interactive=False
            )
        
        # Voice prompts section
        gr.Markdown("### 🎤 Individual Voice Prompts")
        with gr.Row():
            with gr.Column():
                s_prompt = gr.Textbox(label="🎼 Soprano", value="Make soprano more lyrical", lines=2)
            with gr.Column():
                a_prompt = gr.Textbox(label="🎼 Alto", value="Add rich harmonies", lines=2)
            with gr.Column():
                t_prompt = gr.Textbox(label="🎼 Tenor", value="Enhance with warm tones", lines=2)
            with gr.Column():
                b_prompt = gr.Textbox(label="🎼 Bass", value="Create solid foundation", lines=2)
        
        # Voice preview section
        gr.Markdown("### 🎵 Individual Voice Previews")
        with gr.Row():
            with gr.Column():
                s_audio = gr.Audio(label="🎼 Soprano Preview", interactive=False)
                s_info = gr.Textbox(label="📊 Soprano Info", lines=3, interactive=False)
            with gr.Column():
                a_audio = gr.Audio(label="🎼 Alto Preview", interactive=False)
                a_info = gr.Textbox(label="📊 Alto Info", lines=3, interactive=False)
            with gr.Column():
                t_audio = gr.Audio(label="🎼 Tenor Preview", interactive=False)
                t_info = gr.Textbox(label="📊 Tenor Info", lines=3, interactive=False)
            with gr.Column():
                b_audio = gr.Audio(label="🎼 Bass Preview", interactive=False)
                b_info = gr.Textbox(label="📊 Bass Info", lines=3, interactive=False)
        
        # Generate button
        with gr.Row():
            generate_btn = gr.Button("🎯 Generate Voice Audio Files", variant="primary", size="lg")
        
        # Output section
        gr.Markdown("### 📤 Download Results")
        with gr.Row():
            with gr.Column(scale=2):
                output_file = gr.File(label="📄 Harmonized MusicXML", interactive=False)
            with gr.Column(scale=1):
                master_audio = gr.Audio(label="🎵 Master Mix (All Voices)", interactive=False)
            with gr.Column(scale=1):
                output_summary = gr.Textbox(
                    label="📝 Summary",
                    lines=10,
                    max_lines=15,
                    interactive=False,
                    show_copy_button=True
                )
        
        # State management
        prompts_state = gr.State({})
        
        # Event handlers
        def update_prompts(s_prompt, a_prompt, t_prompt, b_prompt):
            return {"S": s_prompt, "A": a_prompt, "T": t_prompt, "B": b_prompt}
        
        def generate_ultra_minimal_harmonization(score_file, prompts, base_tuning=None):
            """Ultra-minimal harmonization with voice previews."""
            if base_tuning is None:
                base_tuning = 432.0
            
            # Load score
            from core.score import load_musicxml
            score = load_musicxml(score_file)
            
            # Apply harmonization (very basic)
            llm = DummyLLM()
            llm_suggestions = llm.harmonize_multi_voice(prompts)
            
            # Apply suggestions to score (first 4 measures only)
            for voice, suggestion in llm_suggestions.items():
                measure_num = suggestion.get('measure', 1)
                if measure_num <= 4:  # Only modify first 4 measures
                    new_root = suggestion.get('root', 'C')
                    try:
                        replace_chord_in_measure(score, measure_num, new_root, 'major')
                    except Exception as e:
                        print(f"Could not replace chord in measure {measure_num}: {e}")
            
            # Save harmonized score
            tmp_xml = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
            write_musicxml(score, tmp_xml.name)
            
            # Generate individual voice previews (10 seconds each)
            voice_audios = {}
            voice_infos = {}
            for voice in ['S', 'A', 'T', 'B']:
                voice_audio = viewer.generate_voice_audio(score, voice, base_tuning, duration=10)
                if voice_audio:
                    voice_infos[voice] = viewer.get_voice_info(voice)
            
            # Create summary
            summary = f"""✅ **Ultra-Minimal Harmonization Complete**

**📊 Score Analysis:**
Parts: {len(score.parts)}
Measures: {len(first_part.getElementsByClass('Measure') if score.parts else [])}

**🎵 Applied Changes:**
- Voice prompts processed for S/A/T/B
- Chord replacements in measures 1-4
- Base tuning: {base_tuning} Hz

**🎵 Audio Generated:**
- Individual voices: {len([v for v in voice_audios if voice_audios.get(v) is not None])}

**📁 Output Files:**
- MusicXML: Ready for download
- Voice audio: {len([v for v in voice_audios if voice_audios.get(v) is not None])}

**🎯 Technical Details:**
- Audio duration: ~10s per voice
- Format: WAV, 44.1kHz, 16-bit stereo
- Base tuning: {base_tuning} Hz

**Features Available:**
- Individual voice audio generation
- Basic score visualization
- Simple but functional interface
- Stable operation with minimal dependencies
"""
            
            return {
                'harmonized_xml': str(Path(tmp_xml.name)),
                'voice_audios': voice_audios,
                'summary': summary
            }
            
        except Exception as e:
            return {
                'harmonized_xml': None,
                'voice_audios': {},
                'summary': f"❌ **Error:** {str(e)}"
            }
        
        # Event handlers
        for prompt_input in [s_prompt, a_prompt, t_prompt, b_prompt]:
            prompt_input.change(
                fn=update_prompts,
                inputs=[s_prompt, a_prompt, t_prompt, b_prompt],
                outputs=[prompts_state]
            )
        
        tuning_slider.change(
            fn=lambda x: f"{x} Hz",
            inputs=[tuning_slider],
            outputs=[tuning_display]
        )
        
        generate_btn.click(
            fn=generate_ultra_minimal_harmonization,
            inputs=[score_input, prompts_state, tuning_slider],
            outputs=[
                output_file, 
                *list(voice_audios.values()),
                output_summary
            ]
        )
    
    return app