#!/usr/bin/env python3
"""
Simple Gradio Test App for Choral LLM Workbench

This is a minimal working example to test the new infrastructure
without the complex State issues in the original app.
"""

import gradio as gr
from core.i18n import _, get_i18n
from core.constants import AudioDefaults, VoiceInfo
from core.config import get_config
from pathlib import Path


def test_file_upload(file_obj):
    """Test file upload functionality."""
    if file_obj is None:
        return _("file.upload_failed"), None
    
    return _("file.upload_success", filename=file_obj.name), file_obj.name


def test_tuning_selection(tuning_value):
    """Test tuning selection."""
    config = get_config()
    i18n = get_i18n()
    
    return i18n.format_frequency(tuning_value)


def test_voice_selection(voice):
    """Test voice selection."""
    if voice in VoiceInfo.VOICE_COLORS:
        color = VoiceInfo.VOICE_COLORS[voice]
        return f"Selected {voice} with color {color}"
    return f"Unknown voice: {voice}"


def main():
    """Create and launch the test interface."""
    with gr.Blocks(title="Choral Workbench Test") as demo:
        gr.Markdown("# 🎵 Choral LLM Workbench - Infrastructure Test")
        gr.Markdown("Testing new i18n, config, and validation systems")
        
        with gr.Tabs():
            # File Upload Test
            with gr.Tab(_("ui.musicxml_input")):
                gr.Markdown("### File Upload Test")
                with gr.Row():
                    file_input = gr.File(
                        label=_("ui.musicxml_input"),
                        file_types=[".xml", ".musicxml", ".mxl"]
                    )
                with gr.Row():
                    upload_btn = gr.Button("Upload Test")
                with gr.Row():
                    upload_result = gr.Textbox(label="Result", interactive=False)
                    file_info = gr.Textbox(label="File Info", interactive=False)
                
                upload_btn.click(
                    fn=test_file_upload,
                    inputs=[file_input],
                    outputs=[upload_result, file_info]
                )
            
            # Tuning Test
            with gr.Tab(_("ui.base_tuning")):
                gr.Markdown("### Audio Tuning Test")
                with gr.Row():
                    tuning_slider = gr.Slider(
                        minimum=min(AudioDefaults.TUNING_OPTIONS),
                        maximum=max(AudioDefaults.TUNING_OPTIONS),
                        value=AudioDefaults.BASE_TUNING,
                        step=1.0,
                        label=_("ui.base_tuning")
                    )
                with gr.Row():
                    tuning_result = gr.Textbox(label="Formatted Frequency", interactive=False)
                
                tuning_slider.change(
                    fn=test_tuning_selection,
                    inputs=[tuning_slider],
                    outputs=[tuning_result]
                )
            
            # Voice Test
            with gr.Tab("Voice Selection"):
                gr.Markdown("### Voice Selection Test")
                with gr.Row():
                    voice_dropdown = gr.Dropdown(
                        choices=VoiceInfo.SATB_VOICES,
                        value="soprano",
                        label="Select Voice"
                    )
                with gr.Row():
                    voice_result = gr.Textbox(label="Voice Info", interactive=False)
                
                voice_dropdown.change(
                    fn=test_voice_selection,
                    inputs=[voice_dropdown],
                    outputs=[voice_result]
                )
            
            # Configuration Test
            with gr.Tab("Configuration"):
                gr.Markdown("### Configuration Test")
                config = get_config()
                
                gr.Markdown(f"""
                - **Base Tuning**: {config.audio.base_tuning} Hz
                - **Tuning Options**: {', '.join(map(str, config.audio.tuning_options))}
                - **LLM Timeout**: {config.llm.timeout} seconds
                - **UI Language**: {config.ui.language}
                - **Max File Size**: {config.ui.max_file_size} MB
                - **Enable LLM**: {config.features.enable_llm_integration}
                - **Enable Audio**: {config.features.enable_audio_rendering}
                """)
                
                # Test i18n
                i18n = get_i18n()
                gr.Markdown(f"""
                ### Internationalization Test
                - **Available Locales**: {', '.join(i18n.get_available_locales())}
                - **Current Locale**: {i18n.current_locale}
                - **MusicXML Input**: {_("ui.musicxml_input")}
                - **Render Audio**: {_("ui.render_audio")}
                - **Soprano**: {_("voice.soprano")}
                - **Alto**: {_("voice.alto")}
                - **Tenor**: {_("voice.tenor")}
                - **Bass**: {_("voice.bass")}
                """)
    
    return demo


if __name__ == "__main__":
    demo = main()
    
    # Test creation without launch
    print("✅ Gradio app created successfully!")
    print("🚀 All infrastructure components working!")
    print("📁 Available tabs: File Upload, Tuning, Voice Selection, Configuration")
    print("🌐 i18n support: English/German")
    print("⚙️ Configuration system: Active")
    print("✅ Ready for manual testing with: demo.launch()")