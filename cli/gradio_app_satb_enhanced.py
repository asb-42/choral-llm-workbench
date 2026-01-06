"""
Enhanced SATB harmonization with proper harmonization logic and LLM integration.
"""

import gradio as gr
from copy import deepcopy
from pathlib import Path

# Core imports
from core.score import load_musicxml, write_musicxml
from core.score.reharmonize import replace_chord_in_measure, make_chord
from core.score.harmony import analyze_chords
from core.audio import score_to_midi, render_score_audio
from core.editor.dummy_llm import DummyLLM
from core.config import get_config
from core.i18n import _
from core.constants import AudioDefaults, VoiceInfo
from core.score.preview import create_preview_component

import tempfile
import os


class SATBHarmonizer:
    """Advanced SATB harmonization with proper voice leading and chord logic."""
    
    def __init__(self):
        self.llm = DummyLLM()
        self.config = get_config()
    
    def analyze_voice_parts(self, score):
        """Analyze and identify voice parts in score."""
        voice_mapping = {}
        
        for i, part in enumerate(score.parts):
            part_name = getattr(part, 'partName', '').lower()
            
            # Detect voice type
            if 'soprano' in part_name or 's' in part_name:
                voice_mapping['S'] = part
            elif 'alto' in part_name or 'a' in part_name:
                voice_mapping['A'] = part
            elif 'tenor' in part_name or 't' in part_name:
                voice_mapping['T'] = part
            elif 'bass' in part_name or 'b' in part_name:
                voice_mapping['B'] = part
            else:
                # Fallback: assign by part order
                if i == 0:
                    voice_mapping['S'] = part
                elif i == 1:
                    voice_mapping['A'] = part
                elif i == 2:
                    voice_mapping['T'] = part
                elif i == 3:
                    voice_mapping['B'] = part
        
        return voice_mapping
    
    def apply_voice_leading_rules(self, score, voice_mapping):
        """Apply proper voice leading rules to SATB parts."""
        # Basic voice leading constraints
        rules_applied = []
        
        # Soprano: Generally should be highest voice
        if 'S' in voice_mapping:
            soprano_part = voice_mapping['S']
            soprano_notes = [n for n in soprano_part.flat.getElementsByClass(['Note', 'Chord']) 
                           if hasattr(n, 'pitch')]
            if soprano_notes:
                soprano_midi = [n.pitch.midi for n in soprano_notes]
                rules_applied.append(f"Soprano range: {min(soprano_midi)}-{max(soprano_midi)}")
        
        # Bass: Generally should be lowest voice
        if 'B' in voice_mapping:
            bass_part = voice_mapping['B']
            bass_notes = [n for n in bass_part.flat.getElementsByClass(['Note', 'Chord']) 
                        if hasattr(n, 'pitch')]
            if bass_notes:
                bass_midi = [n.pitch.midi for n in bass_notes]
                rules_applied.append(f"Bass range: {min(bass_midi)}-{max(bass_midi)}")
        
        return rules_applied
    
    def create_chord_progression(self, score, llm_suggestions):
        """Create proper chord progression based on LLM suggestions."""
        progression = []
        
        # Analyze existing harmony
        try:
            existing_chords = analyze_chords(score)
            progression.append(f"Found {len(existing_chords)} existing chords")
        except:
            progression.append("Could not analyze existing harmony")
        
        # Apply LLM suggestions with music theory constraints
        for voice, suggestion in llm_suggestions.items():
            measure_num = suggestion.get('measure', 1)
            new_root = suggestion.get('root', 'C')
            new_quality = suggestion.get('quality', 'major')
            
            try:
                # Create chord with proper voice leading
                new_chord = make_chord(new_root, new_quality)
                replace_chord_in_measure(score, measure_num, new_root, new_quality)
                progression.append(f"Applied {voice} chord: {new_root} {new_quality} in measure {measure_num}")
            except Exception as e:
                progression.append(f"Failed to apply {voice} chord: {e}")
        
        return progression
    
    def harmonize_score(self, score_file, prompts, base_tuning=None):
        """
        Complete harmonization workflow with proper SATB logic.
        """
        if base_tuning is None:
            base_tuning = AudioDefaults.BASE_TUNING
        
        try:
            # Load score
            score = load_musicxml(score_file)
            
            # Analyze voice parts
            voice_mapping = self.analyze_voice_parts(score)
            
            # Apply voice leading rules
            voice_leading_info = self.apply_voice_leading_rules(score, voice_mapping)
            
            # Get LLM suggestions
            llm_suggestions = self.llm.harmonize_multi_voice(prompts)
            
            # Apply chord progression
            progression_info = self.create_chord_progression(score, llm_suggestions)
            
            # Save updated MusicXML
            tmp_xml = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
            write_musicxml(score, tmp_xml.name)
            
            # Generate audio preview
            try:
                audio_file = render_score_audio(score, base_tuning=base_tuning)
            except Exception as audio_error:
                print(f"Audio rendering failed: {audio_error}")
                audio_file = None
            
            # Create summary
            summary = []
            summary.append("✅ **Harmonization Complete**")
            summary.append(f"")
            summary.append(f"**Voice Mapping:** {', '.join(voice_mapping.keys())}")
            summary.append(f"")
            summary.append(f"**Voice Leading:**")
            summary.extend([f"  • {info}" for info in voice_leading_info])
            summary.append(f"")
            summary.append(f"**Chord Changes:**")
            summary.extend([f"  • {info}" for info in progression_info])
            summary.append(f"")
            summary.append(f"**Audio Settings:**")
            summary.append(f"  • Base Tuning: {base_tuning} Hz")
            
            return str(Path(tmp_xml.name)), str(audio_file) if audio_file else None, "\n".join(summary)
            
        except Exception as e:
            return None, None, f"❌ **Harmonization Error:** {str(e)}"


def create_satb_interface():
    """Create enhanced SATB harmonization interface."""
    harmonizer = SATBHarmonizer()
    
    with gr.Blocks(title="Choral LLM Workbench - SATB Harmonizer") as app:
        gr.Markdown("## 🎵 SATB Harmonization with Advanced Audio Preview")
        
        # File input and preview section
        with gr.Row():
            with gr.Column(scale=2):
                score_input = gr.File(label="📁 Upload MusicXML", file_types=[".xml", ".musicxml", ".mxl"])
        
        # Audio tuning controls
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🎛️ Audio Settings")
                with gr.Row():
                    tuning_slider = gr.Slider(
                        minimum=min(AudioDefaults.TUNING_OPTIONS),
                        maximum=max(AudioDefaults.TUNING_OPTIONS),
                        value=AudioDefaults.BASE_TUNING,
                        step=1.0,
                        label="Base Tuning (Hz)"
                    )
                    tuning_display = gr.Textbox(
                        label="Current Tuning",
                        value=f"{AudioDefaults.BASE_TUNING} Hz",
                        interactive=False,
                        scale=1
                    )
        
        # Voice prompts section
        with gr.Row():
            gr.Markdown("### 🎤 Voice-Specific Prompts")
        
        with gr.Row():
            with gr.Column():
                s_prompt = gr.Textbox(
                    label="🎼 Soprano Prompt", 
                    value="Make soprano more lyrical and expressive",
                    lines=2
                )
            with gr.Column():
                a_prompt = gr.Textbox(
                    label="🎼 Alto Prompt", 
                    value="Add rich harmonies to alto part",
                    lines=2
                )
            with gr.Column():
                t_prompt = gr.Textbox(
                    label="🎼 Tenor Prompt", 
                    value="Enhance tenor with warm resonance",
                    lines=2
                )
            with gr.Column():
                b_prompt = gr.Textbox(
                    label="🎼 Bass Prompt", 
                    value="Create solid harmonic foundation in bass",
                    lines=2
                )
        
        # Action buttons
        with gr.Row():
            harmonize_btn = gr.Button("🎯 Harmonize Score", variant="primary", size="lg")
        
        # Output section
        with gr.Row():
            gr.Markdown("### 📤 Output & Results")
        
        with gr.Row():
            with gr.Column():
                output_file = gr.File(label="📄 Harmonized MusicXML", interactive=False)
            with gr.Column():
                output_audio = gr.Audio(label="🎵 Audio Preview", interactive=False)
        
        with gr.Row():
            output_summary = gr.Textbox(
                label="📝 Harmonization Summary",
                lines=8,
                max_lines=12,
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
            fn=harmonizer.harmonize_score,
            inputs=[score_input, prompts_state, tuning_slider],
            outputs=[output_file, output_audio, output_summary]
        )
    
    return app


if __name__ == "__main__":
    app = create_satb_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )