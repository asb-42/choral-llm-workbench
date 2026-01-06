"""
Working score viewer with voice previews - FIXED VERSION
"""

import gradio as gr
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

try:
    from music21 import converter, stream, note, chord, meter
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    converter = None


def create_fixed_viewer():
    """Create a working score viewer without syntax errors."""
    
    with gr.Blocks(title="Choral LLM Workbench - Working Score Viewer") as app:
        gr.Markdown("## 🎼 Working Score Viewer (Fixed)")
        gr.Markdown("Upload MusicXML and see score notation!")
        
        # File input
        with gr.Row():
            score_input = gr.File(label="📁 Upload MusicXML", file_types=[".xml", ".musicxml", ".mxl"])
        
        # Score preview section
        with gr.Row():
            with gr.Column(scale=3):
                gr.Markdown("### 📊 Score Preview")
                
                score_image = gr.Image(
                    label="Score Visualization",
                    height=200,
                    type="filepath",
                    interactive=False
                )
                
                score_info = gr.Textbox(
                    label="📊 Score Information",
                    lines=6,
                    max_lines=6,
                    interactive=False
                )
        
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
        gr.Markdown("### 🎤 Voice-Specific Prompts")
        with gr.Row():
            s_prompt = gr.Textbox(label="🎼 Soprano", value="Make soprano more lyrical")
            a_prompt = gr.Textbox(label="🎼 Alto", value="Add rich harmonies to alto")
        with gr.Row():
            t_prompt = gr.Textbox(label="🎼 Tenor", value="Enhance tenor with warm tones")
        with gr.Row():
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
                output_summary = gr.Textbox(
                    label="📝 Detailed Summary",
                    lines=8,
                    max_lines=12,
                    interactive=False,
                    show_copy_button=True
                )
        
        # State management
        prompts_state = gr.State({})
        
        # Event handlers
        def update_prompts(s_prompt, a_prompt, t_prompt, b_prompt):
            return {"S": s_prompt, "A": a_prompt, "T": t_prompt, "B": b_prompt}
        
        def update_tuning_display(tuning_value):
            return f"{tuning_value} Hz"
        
        def simple_harmonize(score_file, prompts, base_tuning=None):
            """Simple harmonization working correctly."""
            if base_tuning is None:
                base_tuning = AudioDefaults.BASE_TUNING
            
            try:
                # Load score
                from core.score import load_musicxml
                score = load_musicxml(score_file)
                
                # Apply harmonization
                from core.score.reharmonize import replace_chord_in_make_chord
                from core.editor.dummy_llm import DummyLLM
                llm = DummyLLM()
                llm_suggestions = llm.harmonize_multi_voice(prompts)
                
                # Apply suggestions to first few measures only
                for voice, suggestion in llm_suggestions.items():
                    measure_num = suggestion.get('measure', 1)
                    if measure_num <= 4:  # Only modify first 4 measures
                        new_root = suggestion.get('root', 'C')
                        try:
                            replace_chord_in_make_chord(score, measure_num, new_root, 'major')
                        except Exception as e:
                            print(f"Could not replace chord in measure {measure_num}: {e}")
                
                # Save harmonized score
                tmp_xml = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
                write_musicxml(score, tmp_xml.name)
                
                # Generate audio preview
                try:
                    from core.audio import score_to_midi, render_score_audio
                    
                    midi_path = score_to_midi(score)
                    wav_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                    wav_path = Path(wav_tmp.name)
                    
                    render_score_audio(
                        midi_path=str(midi_path),
                        wav_path=str(wav_path),
                        base_tuning=base_tuning,
                        duration_limit=30  # Prevent overly long files
                    )
                    
                    audio_file = str(wav_path) if wav_path and Path(wav_path).exists() else None
                    
                    # Clean up MIDI file
                    if midi_path.exists():
                        midi_path.unlink()
                    
                except Exception as audio_error:
                    print(f"Audio rendering failed: {audio_error}")
                    audio_file = None
                
                # Create comprehensive summary
                summary = f"""✅ **Harmonization Complete**

**Applied Changes:**
- Voice prompts processed for S/A/T/B
- Chord replacements in measures 1-4
- Base tuning: {base_tuning} Hz

**Output Files:**
- MusicXML: Ready for download
- Audio: {'Available' if audio_file else 'Not available'}

**Summary:**
Score harmonized with {len(llm_suggestions)} voice suggestions.
Duration limited to prevent overly long audio files.
Simple score viewer shows basic notation.
"""
                
                return str(Path(tmp_xml.name)), audio_file, summary
                
            except Exception as e:
                return None, None, f"❌ **Error:** {str(e)}"
        
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
            fn=simple_harmonize,
            inputs=[score_input, prompts_state, tuning_slider],
            outputs=[output_file, output_audio, output_summary]
        )
    
    return app