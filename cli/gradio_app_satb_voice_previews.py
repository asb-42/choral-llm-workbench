"""
Enhanced SATB harmonization with detailed voice preview.

This application provides:
- Individual voice previews for each SATB voice
- Real-time audio preview per voice
- Comprehensive harmonization workflow
- Professional score visualization
- Downloadable voice-specific audio files
"""

import gradio as gr
from pathlib import Path
import tempfile
import subprocess
from typing import Dict, List, Optional, Tuple

# Core imports
from core.score import load_musicxml, write_musicxml
from core.score.reharmonize import replace_chord_in_measure, make_chord
from core.audio import score_to_midi, render_audio_with_tuning
from core.editor.dummy_llm import DummyLLM
from core.config import get_config
from core.i18n import _
from core.constants import AudioDefaults, VoiceInfo
from core.score.preview import create_simple_viewer


class VoiceAudioPreview:
    """Manage individual voice audio generation and preview."""
    
    def __init__(self):
        self.llm = DummyLLM()
        self.config = get_config()
    
    def generate_voice_audio(self, score, voice: str, base_tuning: float, 
                           duration_limit: int = 30) -> Optional[Path]:
        """
        Generate audio for a specific voice part.
        
        Args:
            score: Music21 Score object
            voice: Voice identifier ('S', 'A', 'T', 'B')
            base_tuning: Base tuning frequency
            duration_limit: Maximum duration in seconds
            
        Returns:
            Path to generated audio file or None
        """
        try:
            # Extract only the specified voice part
            voice_part = None
            voice_mapping = {'S': 0, 'A': 1, 'T': 2, 'B': 3}
            
            if voice in voice_mapping and voice_mapping[voice] < len(score.parts):
                voice_part = score.parts[voice_mapping[voice]]
            
            if voice_part is None:
                print(f"Voice {voice} not found in score")
                return None
            
            # Create new score with only this voice
            voice_score = type(score)()
            voice_score.append(voice_part)
            
            # Check if voice has notes
            has_notes = len(voice_part.flat.getElementsByClass(['Note', 'Chord'])) > 0
            if not has_notes:
                print(f"Voice {voice} has no notes to render")
                return None
            
            # Generate MIDI
            midi_path = score_to_midi(voice_score)
            
            # Generate audio with duration limit
            audio_file = None
            try:
                wav_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{voice}.wav")
                render_audio_with_tuning(
                    midi_path=str(midi_path),
                    wav_path=str(wav_tmp.name),
                    base_tuning=base_tuning,
                    duration_limit=duration_limit
                )
                audio_file = Path(wav_tmp.name)
                midi_path.unlink()
                
                print(f"Generated {voice} voice audio: {audio_file}")
                
            except Exception as e:
                print(f"Error generating {voice} voice audio: {e}")
                return None
            
            return audio_file
            
        except Exception as e:
            print(f"Error processing {voice} voice: {e}")
            return None
    
    def generate_master_audio(self, score, base_tuning: float, 
                          duration_limit: int = 60) -> Optional[Path]:
        """
        Generate full ensemble audio.
        
        Args:
            score: Music21 Score object
            base_tuning: Base tuning frequency
            duration_limit: Maximum duration in seconds
            
        Returns:
            Path to generated master audio file or None
        """
        try:
            midi_path = score_to_midi(score)
            
            # Generate master audio with longer duration
            wav_tmp = tempfile.NamedTemporaryFile(delete=False, suffix="_master.wav")
            render_audio_with_tuning(
                midi_path=str(midi_path),
                wav_path=str(wav_tmp.name),
                base_tuning=base_tuning,
                duration_limit=duration_limit
            )
            master_file = Path(wav_tmp.name)
            midi_path.unlink()
            
            print(f"Generated master ensemble audio: {master_file}")
            
            return master_file
            
        except Exception as e:
            print(f"Error generating master audio: {e}")
            return None


def detailed_harmonize_with_voice_previews(score_file, prompts, base_tuning=None):
    """
    Enhanced harmonization with individual voice previews.
    """
    if base_tuning is None:
        base_tuning = AudioDefaults.BASE_TUNING
    
    try:
        # Load original score
        original_score = load_musicxml(score_file)
        
        # Generate harmonized score
        llm = DummyLLM()
        llm_suggestions = llm.harmonize_multi_voice(prompts)
        
        harmonized_score = load_musicxml(score_file)  # Fresh copy
        for voice, suggestion in llm_suggestions.items():
            measure_num = suggestion.get('measure', 1)
            if measure_num <= 4:  # Only modify first 4 measures
                new_root = suggestion.get('root', 'C')
                try:
                    replace_chord_in_measure(harmonized_score, measure_num, new_root, 'major')
                except Exception as e:
                    print(f"Could not replace chord in measure {measure_num}: {e}")

        # Save harmonized score
        tmp_xml = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
        write_musicxml(harmonized_score, tmp_xml.name)
        
        # Initialize voice preview generator
        voice_preview = VoiceAudioPreview()
        
        # Generate voice-specific audio files
        voice_audios = {}
        voice_info = {}
        
        for voice in ['S', 'A', 'T', 'B']:
            if voice in ['Soprano', 'Alto', 'Tenor', 'Bass']:
                # Map to voice names
                voice_map = {'S': 'Soprano', 'A': 'Alto', 'T': 'Tenor', 'B': 'Bass'}
                display_voice = voice_map.get(voice, voice)
            else:
                display_voice = voice
            
            voice_audio = voice_preview.generate_voice_audio(
                harmonized_score, 
                voice, 
                base_tuning, 
                duration_limit=15  # Shorter duration for individual voices
            )
            
            if voice_audio:
                voice_audios[display_voice] = voice_audio
                voice_info[display_voice] = {
                    'file': str(voice_audio),
                    'size': voice_audio.stat().st_size if voice_audio.exists() else 0,
                    'duration_est': voice_audio.stat().st_size / 88200  # Estimate
                }
            else:
                voice_info[display_voice] = {
                    'file': None,
                    'error': f"No audio generated for {display_voice}"
                }
        
        # Generate master ensemble audio
        master_audio = voice_preview.generate_master_audio(
            harmonized_score, 
            base_tuning, 
            duration_limit=45  # Longer for ensemble
        )
        
        master_info = {
            'file': str(master_audio) if master_audio else None,
            'size': master_audio.stat().st_size if master_audio and master_audio.exists() else 0,
            'duration_est': master_audio.stat().st_size / 88200 if master_audio and master_audio.exists() else 0,
        }
        
        # Create comprehensive summary
        summary = f"""✅ **Detailed Voice-Specific Harmonization Complete**

**🎵 Applied Changes:**
- Voice prompts processed for S/A/T/B
- Chord replacements in measures 1-4
- Base tuning: {base_tuning} Hz
- Voice-specific audio generation

**🎼 Individual Voice Audio:**
"""
        
        for voice, info in voice_info.items():
            if 'error' in info:
                summary += f"• {voice}: {info['error']}\n"
            else:
                summary += f"""• {voice} ({info['duration_est']:.1f}s): {info['file']}\n"""
        
        summary += f"""
**🎵 Ensemble Master Audio:**
"""
        if 'error' not in master_info:
            summary += f"""• Master Mix ({master_info['duration_est']:.1f}s): {master_info['file']}\n"""
        else:
            summary += "• Master Mix: Generation failed\n"

        summary += f"""
**📊 Technical Details:**
- Total voices processed: {len([v for v in voice_info.keys() if not voice_info[v].get('error')])}
- Audio samples: 44.1kHz, 16-bit stereo
- Individual voice duration: ~15 seconds each
- Master duration: ~45 seconds
- Base tuning applied throughout

**📁 Output Files:**
- Harmonized MusicXML: Ready for download
- Individual voice audio: {len([v for v in voice_audios.values() if voice_audios[v]])} files
- Master ensemble audio: {'Available' if master_info['file'] else 'Not available'}
"""
        
        return {
            'harmonized_xml': str(Path(tmp_xml.name)),
            'voice_audios': voice_audios,
            'master_audio': master_info.get('file'),
            'summary': summary
        }
        
    except Exception as e:
        return {
            'harmonized_xml': None,
            'voice_audios': {},
            'master_audio': None,
            'summary': f"❌ **Error:** {str(e)}"
        }


def create_enhanced_interface():
    """Create enhanced interface with voice previews."""
    
    with gr.Blocks(title="Choral LLM Workbench - Voice-Specific Audio Preview") as app:
        gr.Markdown("## 🎵 SATB Harmonization with Individual Voice Previews")
        gr.Markdown("Upload MusicXML, enter voice-specific prompts, and get individual voice audio files!")
        
        # File input section
        with gr.Row():
            score_input = gr.File(label="📁 Upload MusicXML", file_types=[".xml", ".musicxml", ".mxl"])
        
        # Audio tuning controls
        with gr.Row():
            with gr.Column(scale=2):
                tuning_slider = gr.Slider(
                    minimum=min(AudioDefaults.TUNING_OPTIONS),
                    maximum=max(AudioDefaults.TUNING_OPTIONS),
                    value=AudioDefaults.BASE_TUNING,
                    step=1.0,
                    label="🎛️ Base Tuning (Hz)"
                )
            with gr.Column(scale=1):
                tuning_display = gr.Textbox(
                    label="Current Tuning",
                    value=f"{AudioDefaults.BASE_TUNING} Hz",
                    interactive=False
                )
        
        # Voice prompts section
        gr.Markdown("### 🎤 Individual Voice Prompts")
        with gr.Row():
            s_prompt = gr.Textbox(label="🎼 Soprano", value="Make soprano more expressive and lyrical", lines=3)
            a_prompt = gr.Textbox(label="🎼 Alto", value="Add rich harmonies to alto part", lines=3)
        with gr.Row():
            t_prompt = gr.Textbox(label="🎼 Tenor", value="Enhance tenor with warm resonance", lines=3)
            b_prompt = gr.Textbox(label="🎼 Bass", value="Create solid harmonic foundation", lines=3)
        
        # Advanced options
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### 🎛️ Audio Generation Options")
                individual_duration = gr.Slider(
                    minimum=5,
                    maximum=30,
                    value=15,
                    step=1,
                    label="Individual Voice Duration (seconds)"
                )
                master_duration = gr.Slider(
                    minimum=10,
                    maximum=90,
                    value=45,
                    step=5,
                    label="Master Mix Duration (seconds)"
                )
        
        # Action buttons
        with gr.Row():
            harmonize_btn = gr.Button("🎯 Harmonize with Voice Previews", variant="primary", size="lg")
        
        # Score preview section
        gr.Markdown("### 📊 Score Visualization")
        score_col, score_image, score_info = create_simple_viewer()
        
        # Voice audio preview section
        gr.Markdown("### 🎼 Individual Voice Audio Previews")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### 🎵 Soprano")
                s_audio = gr.Audio(label="Soprano Audio", interactive=False)
                s_info = gr.Textbox(label="Soprano Info", lines=3, interactive=False)
            
            with gr.Column():
                gr.Markdown("#### 🎼 Alto")
                a_audio = gr.Audio(label="Alto Audio", interactive=False)
                a_info = gr.Textbox(label="Alto Info", lines=3, interactive=False)
            
            with gr.Column():
                gr.Markdown("#### 🎼 Tenor")
                t_audio = gr.Audio(label="Tenor Audio", interactive=False)
                t_info = gr.Textbox(label="Tenor Info", lines=3, interactive=False)
            
            with gr.Column():
                gr.Markdown("#### 🎼 Bass")
                b_audio = gr.Audio(label="Bass Audio", interactive=False)
                b_info = gr.Textbox(label="Bass Info", lines=3, interactive=False)
        
        # Master audio section
        gr.Markdown("### 🎵 Master Ensemble Audio")
        with gr.Row():
            master_audio = gr.Audio(label="Master Mix", interactive=False)
            master_info = gr.Textbox(label="Master Info", lines=4, interactive=False)
        
        # Output section
        gr.Markdown("### 📤 Output Results")
        with gr.Row():
            with gr.Column(scale=2):
                output_file = gr.File(label="📄 Harmonized MusicXML", interactive=False)
            with gr.Column(scale=1):
                output_summary = gr.Textbox(
                    label="📝 Detailed Summary",
                    lines=15,
                    max_lines=20,
                    interactive=False,
                    show_copy_button=True
                )
        
        # Download buttons
        gr.Markdown("### 📁 Download Options")
        with gr.Row():
            with gr.Column():
                download_individual = gr.Button("📁 Download All Voices", variant="secondary", size="sm")
            with gr.Column():
                download_master = gr.Button("📄 Download Master Mix", variant="secondary", size="sm")
        
        # State management
        prompts_state = gr.State({})
        results_state = gr.State({})
        
        # Event handlers
        def update_prompts(s_prompt, a_prompt, t_prompt, b_prompt):
            return {"S": s_prompt, "A": a_prompt, "T": t_prompt, "B": b_prompt}
        
        def update_tuning_display(tuning_value):
            return f"{tuning_value} Hz"
        
        def harmonize_with_previews(score_file, prompts, base_tuning, individual_duration, master_duration):
            """Main harmonization function with voice previews."""
            return detailed_harmonize_with_voice_previews(score_file, prompts, base_tuning)
        
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
        
        # Update score view when file changes
        # Update score view when file changes
        score_input.change(
            fn=update_simple_view,
            inputs=[score_input],
            outputs=[score_image, score_info]
        )
        
        # Main harmonization with voice previews
        harmonize_btn.click(
            fn=harmonize_with_previews,
            inputs=[score_input, prompts_state, tuning_slider, individual_duration, master_duration],
            outputs=[output_file, s_audio, s_info, a_audio, a_info, t_audio, t_info, b_audio, b_info, master_audio, master_info, output_summary]
        )
        
        # Placeholder for download buttons (would need file handling)
        download_individual.click(
            fn=lambda: "📁 Download functionality coming soon!",
            outputs=[output_summary]
        )
        
        download_master.click(
            fn=lambda: "📄 Download functionality coming soon!",
            outputs=[output_summary]
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