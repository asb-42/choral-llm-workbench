"""
Choral Audio Preview App - Working audio-focused preview without visual score limitations.

This app provides:
- MusicXML parsing and audio generation
- Individual voice separation and playback
- Duration control and master audio generation
- Links to other apps
- NO visual score rendering (Gradio limitation - see KNOWN_ISSUES.md)

Focus: WORKING AUDIO FEATURES without Gradio visualization limitations.
"""

import gradio as gr
import tempfile
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any

# Dependency Management (reuse from previous version)
class DependencyManager:
    """Manages automatic dependency checking and installation."""
    
    REQUIRED_PACKAGES = {
        'music21': 'music21>=7.2.1',
        'gradio': 'gradio>=3.40',
        'numpy': 'numpy>=1.25',
        'scipy': 'scipy>=1.12',
        'pygame': 'pygame>=2.6.1',
        'pyfluidsynth': 'pyfluidsynth>=1.3.0'
    }
    
    OPTIONAL_PACKAGES = {
        'matplotlib': 'matplotlib>=3.5.0'
    }
    
    @classmethod
    def check_and_install_dependencies(cls):
        """Check dependencies and install missing ones."""
        print("🔍 Checking dependencies...")
        
        missing_required = []
        missing_optional = []
        
        # Check required packages
        for package, requirement in cls.REQUIRED_PACKAGES.items():
            if not cls._check_package(package):
                missing_required.append(requirement)
        
        # Check optional packages
        for package, requirement in cls.OPTIONAL_PACKAGES.items():
            if not cls._check_package(package):
                missing_optional.append(requirement)
        
        # Install missing required packages
        if missing_required:
            print(f"📦 Installing missing required packages: {', '.join(missing_required)}")
            cls._install_packages(missing_required)
        
        # Install missing optional packages
        if missing_optional:
            print(f"📦 Installing missing optional packages: {', '.join(missing_optional)}")
            cls._install_packages(missing_optional)
        
        if not missing_required and not missing_optional:
            print("✅ All dependencies already installed")
        
        print("🎯 Dependency check completed\n")
    
    @staticmethod
    def _check_package(package_name):
        """Check if a package is installed."""
        try:
            __import__(package_name)
            return True
        except ImportError:
            return False
    
    @staticmethod
    def _install_packages(packages):
        """Install packages using pip."""
        for package in packages:
            try:
                print(f"  Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"  ✅ {package} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Failed to install {package}: {e}")
                return False
        return True

# Check and install dependencies before importing
DependencyManager.check_and_install_dependencies()

# Core imports
try:
    from music21 import converter, stream, note, chord, meter
    from music21.midi.translate import streamToMidiFile
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    converter = None

# Audio generation imports
try:
    import fluidsynth
    FLUIDSYNTH_AVAILABLE = True
except ImportError:
    FLUIDSYNTH_AVAILABLE = False
    fluidsynth = None

# Audio handling
try:
    import numpy as np
    from scipy.io import wavfile
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    np = None
    wavfile = None


class WorkingAudioPreview:
    """Working audio-only preview with functional voice separation."""
    
    def __init__(self):
        self.current_score = None
        self.score_info = {}
        self.temp_dir = tempfile.mkdtemp()
        
        # Default soundfont path
        self.soundfont_path = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
        if not os.path.exists(self.soundfont_path):
            self.soundfont_path = None
    
    def load_score(self, file_path: str) -> bool:
        """Load and parse MusicXML score."""
        if not MUSIC21_AVAILABLE:
            return False
        
        try:
            self.current_score = converter.parse(file_path)
            self._extract_score_info()
            return True
        except Exception as e:
            print(f"Error loading score: {e}")
            return False
    
    def _extract_score_info(self):
        """Extract basic score information."""
        if not self.current_score:
            return
        
        self.score_info = {
            'parts': 0,
            'measures': 0,
            'part_names': [],
            'part_data': []
        }
        
        if hasattr(self.current_score, 'parts') and len(self.current_score.parts) > 0:
            self.score_info['parts'] = len(self.current_score.parts)
            
            # Extract part info
            for i, part in enumerate(self.current_score.parts[:4]):  # Limit to 4 parts
                part_name = getattr(part, 'partName', f'Voice {i+1}')
                self.score_info['part_names'].append(part_name)
                
                # Count measures in this part
                measures = part.getElementsByClass('Measure')
                if len(measures) > self.score_info['measures']:
                    self.score_info['measures'] = len(measures)
    
    def generate_audio_for_voice(self, voice_index: int, duration_seconds: int = 15) -> Optional[str]:
        """Generate audio for a specific voice."""
        if not FLUIDSYNTH_AVAILABLE or not self.soundfont_path:
            print("❌ FluidSynth or soundfont not available")
            return None
        
        if voice_index >= len(self.score_info['part_names']):
            print(f"❌ Voice index {voice_index} out of range")
            return None
        
        try:
            # Extract the specific part
            if voice_index < len(self.current_score.parts):
                part = self.current_score.parts[voice_index]
                
                # Create temporary MIDI file
                midi_path = os.path.join(self.temp_dir, f"voice_{voice_index}.mid")
                mf = streamToMidiFile(part)
                mf.open(midi_path, 'wb')
                mf.write()
                mf.close()
                
                # Generate audio from MIDI
                audio_path = os.path.join(self.temp_dir, f"voice_{voice_index}.wav")
                
                # Use pyfluidsynth to convert MIDI to WAV
                from pyfluidsynth import Synth, MidiFile
                fl = Synth()
                if fl.sfload(self.soundfont_path) == -1:
                    print(f"❌ Failed to load soundfont: {self.soundfont_path}")
                    return None
                
                # Load MIDI and render to audio
                midi_data = MidiFile(midi_path)
                audio_data = fl.midi_to_audio(midi_data, duration_seconds)
                
                # Save as WAV
                wavfile.write(audio_path, 44100, audio_data)
                
                print(f"✅ Generated audio for voice {voice_index}: {audio_path}")
                return audio_path
            
        except Exception as e:
            print(f"❌ Error generating audio for voice {voice_index}: {e}")
            return None
    
    def generate_master_audio(self, duration_seconds: int = 15) -> Optional[str]:
        """Generate audio for all voices combined."""
        if not FLUIDSYNTH_AVAILABLE or not self.soundfont_path:
            print("❌ FluidSynth or soundfont not available")
            return None
        
        try:
            # Create temporary MIDI file for full score
            midi_path = os.path.join(self.temp_dir, "master.mid")
            mf = streamToMidiFile(self.current_score)
            mf.open(midi_path, 'wb')
            mf.write()
            mf.close()
            
            # Generate audio from MIDI
            audio_path = os.path.join(self.temp_dir, "master.wav")
            
            # Use pyfluidsynth to convert MIDI to WAV
            from pyfluidsynth import Synth, MidiFile
            fl = Synth()
            if fl.sfload(self.soundfont_path) == -1:
                print(f"❌ Failed to load soundfont: {self.soundfont_path}")
                return None
            
            # Load MIDI and render to audio
            midi_data = MidiFile(midi_path)
            audio_data = fl.midi_to_audio(midi_data, duration_seconds)
            
            # Save as WAV
            wavfile.write(audio_path, 44100, audio_data)
            
            print(f"✅ Generated master audio: {audio_path}")
            return audio_path
            
        except Exception as e:
            print(f"❌ Error generating master audio: {e}")
            return None
    
    def get_score_summary(self) -> str:
        """Get formatted score summary."""
        if not self.score_info:
            return "No score loaded"
        
        summary = f"**Score Information**\n"
        summary += f"Parts: {self.score_info['parts']}\n"
        summary += f"Measures: {self.score_info['measures']}\n"
        summary += f"Part Names: {', '.join(self.score_info['part_names'])}\n"
        
        # Add availability info
        summary += f"\n**Audio Generation**\n"
        summary += f"FluidSynth: {'Available' if FLUIDSYNTH_AVAILABLE else 'Not Available'}\n"
        summary += f"Soundfont: {'Found' if self.soundfont_path else 'Not Found'}\n"
        
        if not FLUIDSYNTH_AVAILABLE or not self.soundfont_path:
            summary += f"\n⚠️ Audio generation requires FluidSynth and soundfont"
        
        return summary


def create_working_audio_interface():
    """Create working audio-only interface."""
    
    with gr.Blocks(title="Choral LLM Workbench - Working Audio Preview") as app:
        gr.Markdown("## 🎵 Choral Audio Preview (Working)")
        gr.Markdown("""
        **Functional audio preview with voice separation.**
        
        ⚠️ **Note:** Visual score rendering is not possible with Gradio due to framework limitations.
        See `KNOWN_ISSUES.md` for details on this technical constraint and planned solutions.
        
        ✅ **Working Features:**
        - Upload and parse MusicXML files
        - Generate individual voice audio (Soprano, Alto, Tenor, Bass)
        - Generate master ensemble audio
        - Duration control for audio generation
        """)
        
        # File input
        score_input = gr.File(label="📁 Upload MusicXML", file_types=[".xml", ".musicxml", ".mxl"])
        
        # Score information
        with gr.Row():
            score_info = gr.Textbox(
                label="📊 Score Information",
                lines=6,
                interactive=False,
                max_lines=10
            )
        
        # Audio controls
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🎵 Voice Selection")
                
                # Duration control
                duration_slider = gr.Slider(
                    minimum=5,
                    maximum=60,
                    value=15,
                    step=5,
                    label="⏱️ Duration (seconds)"
                )
                
                # Voice selection controls
                with gr.Row():
                    with gr.Column():
                        soprano_check = gr.Checkbox(label="🎵 Soprano", value=True)
                        alto_check = gr.Checkbox(label="🎵 Alto", value=True)
                    with gr.Column():
                        tenor_check = gr.Checkbox(label="🎵 Tenor", value=True)
                        bass_check = gr.Checkbox(label="🎵 Bass", value=True)
                
                # Generate buttons
                with gr.Row():
                    generate_individual_btn = gr.Button("🎧 Generate Individual Voices", variant="primary")
                    generate_master_btn = gr.Button("🎼 Generate Master Audio", variant="secondary")
        
        # Audio outputs
        with gr.Row():
            with gr.Column():
                soprano_audio = gr.Audio(label="Soprano", visible=False)
            with gr.Column():
                alto_audio = gr.Audio(label="Alto", visible=False)
        with gr.Row():
            with gr.Column():
                tenor_audio = gr.Audio(label="Tenor", visible=False)
            with gr.Column():
                bass_audio = gr.Audio(label="Bass", visible=False)
        
        # Master audio
        master_audio = gr.Audio(label="🎼 Full Ensemble", visible=False)
        
        # Links to other apps
        gr.Markdown("### 🔗 Other Applications")
        with gr.Row():
            harmonization_link = gr.Markdown("[🎼 Harmonization App](./gradio_app_satb_simple.py)")
            transformation_link = gr.Markdown("[🔄 Transformation App](./gradio_app_satb_session.py)")
        
        # Initialize previewer
        previewer = WorkingAudioPreview()
        
        # Event handlers
        def update_info(file_obj):
            """Update score information when file is uploaded."""
            if file_obj is None:
                return "No file uploaded"
            
            try:
                # Load and process score
                success = previewer.load_score(file_obj)
                if not success:
                    return "❌ Failed to load score"
                
                # Get score summary
                summary = previewer.get_score_summary()
                return summary
                
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        def generate_individual_audio(file_obj, duration, soprano, alto, tenor, bass):
            """Generate audio for selected voices."""
            if file_obj is None:
                return tuple([None] * 4 + [gr.update(visible=False)] * 4)
            
            try:
                voices_enabled = [soprano, alto, tenor, bass]
                audio_files = [None] * 4
                visibility = [False] * 4
                
                print(f"Generating audio for voices: {voices_enabled}")
                
                for i, enabled in enumerate(voices_enabled):
                    if enabled and i < len(previewer.score_info['part_names']):
                        audio_path = previewer.generate_audio_for_voice(i, duration)
                        if audio_path:
                            audio_files[i] = audio_path
                            visibility[i] = True
                
                return tuple(audio_files) + tuple(
                    gr.update(visible=v) for v in visibility
                )
                
            except Exception as e:
                print(f"Error in generate_individual_audio: {e}")
                return tuple([None] * 8)  # 4 audio files + 4 visibility updates
        
        def generate_master_audio_func(file_obj, duration):
            """Generate master audio."""
            if file_obj is None:
                return None, gr.update(visible=False)
            
            try:
                print("Generating master audio...")
                audio_path = previewer.generate_master_audio(duration)
                if audio_path:
                    return audio_path, gr.update(visible=True)
                else:
                    return None, gr.update(visible=False)
            except Exception as e:
                print(f"Error in generate_master_audio: {e}")
                return None, gr.update(visible=False)
        
        # Connect event handlers
        score_input.change(
            fn=update_info,
            inputs=[score_input],
            outputs=[score_info]
        )
        
        generate_individual_btn.click(
            fn=generate_individual_audio,
            inputs=[score_input, duration_slider, soprano_check, alto_check, tenor_check, bass_check],
            outputs=[soprano_audio, alto_audio, tenor_audio, bass_audio, 
                    soprano_audio, alto_audio, tenor_audio, bass_audio]
        )
        
        generate_master_btn.click(
            fn=generate_master_audio_func,
            inputs=[score_input, duration_slider],
            outputs=[master_audio, master_audio]
        )
    
    return app


if __name__ == "__main__":
    print("🎵 Starting Working Choral Audio Preview App...")
    
    # Check dependencies
    deps_status = {
        'Music21': MUSIC21_AVAILABLE,
        'FluidSynth': FLUIDSYNTH_AVAILABLE,
        'SciPy': SCIPY_AVAILABLE,
        'NumPy': SCIPY_AVAILABLE  # Use SCIPY_AVAILABLE as proxy for numpy
    }
    
    print("📦 Final Dependency Status:")
    all_available = True
    for dep, available in deps_status.items():
        status = "✅" if available else "❌"
        print(f"  {status} {dep}")
        if not available:
            all_available = False
    
    if not all_available:
        print("\n❌ Critical dependencies missing. Automatic installation failed.")
        print("Please install manually:")
        print("  pip install music21 pyfluidsynth scipy numpy")
        sys.exit(1)
    
    print("\n✅ All dependencies satisfied!")
    
    # Create and launch interface
    try:
        app = create_working_audio_interface()
        print("🚀 Launching at http://127.0.0.1:7863")
        print("\n📱 Available Features:")
        print("✅ Upload MusicXML files")
        print("✅ Generate individual voice audio (S, A, T, B)")
        print("✅ Generate master ensemble audio")
        print("✅ Duration control")
        print("⚠️ No visual score preview (see KNOWN_ISSUES.md)")
        
        app.launch(
            server_name="127.0.0.1",
            server_port=7863,
            share=False,
            debug=False
        )
    except Exception as e:
        print(f"\n❌ Failed to launch application: {e}")
        sys.exit(1)