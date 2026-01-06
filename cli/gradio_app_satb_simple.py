"""
Simple fixed Gradio SATB app without problematic components.
"""

import gradio as gr
from pathlib import Path
import tempfile

# Core imports
from core.score import load_musicxml, write_musicxml
from core.score.reharmonize import replace_chord_in_measure, make_chord
from core.audio import score_to_midi, render_score_audio
from core.editor.dummy_llm import DummyLLM
from core.config import get_config
from core.i18n import _
from core.constants import AudioDefaults, VoiceInfo

import os


def simple_harmonize(score_file, prompts, base_tuning=None):
    """
    Simple harmonization without complex preview and duration control.
    """
    if base_tuning is None:
        base_tuning = AudioDefaults.BASE_TUNING
    
    try:
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
        
        # Generate audio preview with duration limit
        try:
            from core.audio import render_audio_with_tuning
            midi_path = score_to_midi(score)
            
            # Create temporary WAV file
            wav_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            wav_path = Path(wav_tmp.name)
            
            # Render with 30 second duration limit
            render_audio_with_tuning(
                midi_path=str(midi_path),
                wav_path=str(wav_path),
                base_tuning=base_tuning,
                duration_limit=30  # Limit to 30 seconds max
            )
            audio_path = str(wav_path)
            
            # Clean up MIDI file
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
"""
        
        return str(Path(tmp_xml.name)), audio_path, summary
        
    except Exception as e:
        return None, None, f"❌ **Error:** {str(e)}"


def create_simple_interface():
    """Create simple but functional SATB interface."""
    
    with gr.Blocks(title="Choral LLM Workbench - Simple SATB") as app:
        gr.Markdown("## 🎵 SATB Harmonization")
        gr.Markdown("Upload a MusicXML file and enter prompts for each voice.")
        
        # File input
        with gr.Row():
            score_input = gr.File(label="📁 Upload MusicXML", file_types=[".xml", ".musicxml", ".mxl"])
        
        # Audio tuning
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
        
        # Voice prompts
        gr.Markdown("### 🎤 Voice-Specific Prompts")
        with gr.Row():
            s_prompt = gr.Textbox(label="🎼 Soprano", value="Make soprano more lyrical")
            a_prompt = gr.Textbox(label="🎼 Alto", value="Add rich harmonies to alto")
        with gr.Row():
            t_prompt = gr.Textbox(label="🎼 Tenor", value="Enhance tenor with warm tones")
            b_prompt = gr.Textbox(label="🎼 Bass", value="Create solid harmonic foundation")
        
        # Action button
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
                lines=10,
                max_lines=15,
                interactive=False
            )
        
        # State management
        prompts_state = gr.State({})
        
        # Event handlers
        def update_prompts(s_prompt, a_prompt, t_prompt, b_prompt):
            return {"S": s_prompt, "A": a_prompt, "T": t_prompt, "B": b_prompt}
        
        def update_tuning_display(tuning_value):
            return f"{tuning_value} Hz"
        
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
        
        harmonize_btn.click(
            fn=simple_harmonize,
            inputs=[score_input, prompts_state, tuning_slider],
            outputs=[output_file, output_audio, output_summary]
        )
    
    return app


if __name__ == "__main__":
    app = create_simple_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False
    )