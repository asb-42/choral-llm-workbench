"""
Choral Score Preview App - Focused test application with score visualization, audio preview, and voice controls.

This app provides:
- MusicXML visual preview as readable score
- Audio preview generation 
- Cursor synchronization between score and audio
- Individual voice separation and playback
- Links to other apps
"""

import gradio as gr
import tempfile
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any

# Dependency Management
class DependencyManager:
    """Manages automatic dependency checking and installation."""
    
    REQUIRED_PACKAGES = {
        'music21': 'music21>=7.2.1',
        'gradio': 'gradio>=3.40',
        'matplotlib': 'matplotlib>=3.5.0',
        'numpy': 'numpy>=1.25',
        'scipy': 'scipy>=1.12',
        'pygame': 'pygame>=2.6.1',
        'pyfluidsynth': 'pyfluidsynth>=1.3.0'
    }
    
    OPTIONAL_PACKAGES = {
        'fluidsynth': 'fluidsynth>=0.3'
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

# Visualization imports
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

# Audio handling
try:
    import numpy as np
    from scipy.io import wavfile
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    np = None
    wavfile = None


class ChoralScorePreview:
    """Focused choral score preview with visualization and audio."""
    
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
                
                # Extract notes for this part
                part_notes = []
                for measure in measures:
                    for element in measure.notesAndRests:
                        if element.isNote:
                            part_notes.append({
                                'name': element.name,
                                'octave': element.octave,
                                'duration': element.duration.quarterLength,
                                'measure': measure.number
                            })
                        elif element.isRest:
                            part_notes.append({
                                'type': 'rest',
                                'duration': element.duration.quarterLength,
                                'measure': measure.number
                            })
                
                self.score_info['part_data'].append(part_notes)
    
    def render_score_image(self, cursor_position: float = 0.0) -> Optional[str]:
        """Render score as visual image."""
        if not MATPLOTLIB_AVAILABLE or not self.current_score:
            return None
        
        try:
            # Create figure for score visualization
            fig, ax = plt.subplots(1, 1, figsize=(14, 8))
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 50)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Title
            ax.text(50, 48, 'Score Preview', fontsize=16, ha='center', weight='bold')
            
            # Draw basic staff lines for each part
            y_positions = [35, 28, 21, 14]  # Y positions for 4 parts
            staff_height = 5
            
            for i, (y_pos, part_name) in enumerate(zip(y_positions, self.score_info['part_names'][:4])):
                # Draw staff lines
                for line_offset in range(5):
                    y = y_pos - line_offset * 1
                    ax.plot([10, 90], [y, y], 'k-', alpha=0.3, linewidth=0.5)
                
                # Part label
                ax.text(2, y_pos - 2, part_name, fontsize=10, va='center')
                
                # Draw some notes as placeholders
                if i < len(self.score_info['part_data']):
                    notes = self.score_info['part_data'][i][:8]  # Show first 8 notes
                    for j, note_info in enumerate(notes[:8]):
                        x = 15 + j * 8
                        
                        if note_info.get('type') != 'rest':
                            # Draw note head
                            note_y = y_pos - 2 + (note_info.get('octave', 4) - 4) * 2
                            circle = plt.Circle((x, note_y), 0.5, color='black', fill=True)
                            ax.add_patch(circle)
                            
                            # Note name
                            ax.text(x, note_y + 3, note_info.get('name', '?'), 
                                   fontsize=8, ha='center')
                        else:
                            # Draw rest symbol
                            ax.plot([x-0.3, x+0.3], [y_pos-2, y_pos-2], 'k-', linewidth=2)
            
            # Add measure numbers
            for i in range(1, 9):
                ax.text(12 + (i-1) * 8, 10, str(i), fontsize=8, ha='center')
            
            # Cursor line at specified position
            cursor_x = 15 + cursor_position * 0.65  # Scale cursor position across score
            ax.axvline(x=cursor_x, color='red', alpha=0.7, linewidth=2, linestyle='--')
            
            # Add cursor position text
            ax.text(cursor_x, 48, f'Cursor: {cursor_position:.0f}%', fontsize=10, 
                   color='red', ha='center', va='bottom')
            
            # Save to temporary file and return path
            import tempfile
            temp_image_path = os.path.join(self.temp_dir, f"score_preview_{cursor_position:.0f}.png")
            plt.savefig(temp_image_path, format='png', dpi=100, bbox_inches='tight')
            plt.close()
            
            return temp_image_path
            
        except Exception as e:
            print(f"Error rendering score: {e}")
            return None
    
    def generate_audio_for_voice(self, voice_index: int, duration_seconds: int = 15) -> Optional[str]:
        """Generate audio for a specific voice."""
        if not FLUIDSYNTH_AVAILABLE or not self.soundfont_path:
            return None
        
        if voice_index >= len(self.score_info['part_names']):
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
                
                # Use fluidsynth to convert MIDI to WAV
                fl = fluidsynth.Synth()
                fl.sfload(self.soundfont_path)
                
                # Load MIDI and render to audio
                midi_data = fluidsynth.MidiFile(midi_path)
                audio_data = fl.midi_to_audio(midi_data, duration_seconds)
                
                # Save as WAV
                wavfile.write(audio_path, 44100, audio_data)
                
                return audio_path
            
        except Exception as e:
            print(f"Error generating audio for voice {voice_index}: {e}")
            return None
    
    def generate_master_audio(self, duration_seconds: int = 15) -> Optional[str]:
        """Generate audio for all voices combined."""
        if not FLUIDSYNTH_AVAILABLE or not self.soundfont_path:
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
            
            # Use fluidsynth to convert MIDI to WAV
            fl = fluidsynth.Synth()
            fl.sfload(self.soundfont_path)
            
            # Load MIDI and render to audio
            midi_data = fluidsynth.MidiFile(midi_path)
            audio_data = fl.midi_to_audio(midi_data, duration_seconds)
            
            # Save as WAV
            wavfile.write(audio_path, 44100, audio_data)
            
            return audio_path
            
        except Exception as e:
            print(f"Error generating master audio: {e}")
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
        
        return summary


def create_preview_interface():
    """Create the focused preview interface."""
    
    with gr.Blocks(title="Choral LLM Workbench - Score Preview") as app:
        gr.Markdown("## 🎼 Choral Score Preview")
        gr.Markdown("Upload MusicXML to visualize score, generate audio, and preview individual voices.")
        
        # File input
        score_input = gr.File(label="📁 Upload MusicXML", file_types=[".xml", ".musicxml", ".mxl"])
        
        # Main content area
        with gr.Row():
            # Left column - Score visualization
            with gr.Column(scale=3):
                score_image = gr.Image(
                    label="📝 Score Preview (with cursor)",
                    height=400
                )
                score_info = gr.Textbox(
                    label="📊 Score Information",
                    lines=4,
                    interactive=False
                )
            
            # Right column - Audio controls
            with gr.Column(scale=2):
                gr.Markdown("### 🎵 Audio Controls")
                
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
        
        # Cursor controls
        with gr.Row():
            cursor_position = gr.Slider(
                minimum=0,
                maximum=100,
                value=0,
                step=1,
                label="📍 Cursor Position (%)",
                visible=False
            )
            cursor_btn = gr.Button("🎯 Move Cursor", variant="secondary", visible=False)
        
        # Links to other apps
        gr.Markdown("### 🔗 Other Applications")
        with gr.Row():
            harmonization_link = gr.Markdown("[🎼 Harmonization App](./gradio_app_satb_simple.py)")
            transformation_link = gr.Markdown("[🔄 Transformation App](./gradio_app_satb_session.py)")
        
        # Initialize previewer
        previewer = ChoralScorePreview()
        
        # Event handlers
        def update_preview(file_obj, cursor_pos=0.0):
            """Update preview when file is uploaded."""
            if file_obj is None:
                return None, "No file uploaded", *[gr.update(visible=False)] * 5
            
            try:
                # Load and process score
                success = previewer.load_score(file_obj)
                if not success:
                    return None, "❌ Failed to load score", *[gr.update(visible=False)] * 5
                
                # Generate visual preview with cursor
                score_image = previewer.render_score_image(cursor_pos)
                score_summary = previewer.get_score_summary()
                
                return (
                    score_image,
                    score_summary,
                    *[gr.update(visible=False)] * 5  # Hide audio outputs initially
                )
                
            except Exception as e:
                return (
                    None,
                    f"❌ Error: {str(e)}",
                    *[gr.update(visible=False)] * 5
                )
        
        def generate_individual_audio(file_obj, duration, soprano, alto, tenor, bass):
            """Generate audio for selected voices."""
            if file_obj is None:
                return tuple([None] * 4)
            
            try:
                voices_enabled = [soprano, alto, tenor, bass]
                audio_files = [None] * 4
                visibility = [False] * 4
                
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
                return tuple([None] * 8)  # 4 audio files + 4 visibility updates
        
        def generate_master_audio_func(file_obj, duration):
            """Generate master audio."""
            if file_obj is None:
                return None, gr.update(visible=False)
            
            try:
                audio_path = previewer.generate_master_audio(duration)
                if audio_path:
                    return audio_path, gr.update(visible=True)
                else:
                    return None, gr.update(visible=False)
            except Exception as e:
                return None, gr.update(visible=False)
        
        def update_cursor_position(file_obj, cursor_pos):
            """Update score image with new cursor position."""
            if file_obj is None:
                return None
            
            try:
                # Regenerate score image with cursor at new position
                score_image = previewer.render_score_image(cursor_pos)
                return score_image
            except Exception as e:
                return None
        
        # Connect event handlers
        score_input.change(
            fn=update_preview,
            inputs=[score_input, cursor_position],
            outputs=[score_image, score_info, soprano_audio, alto_audio, tenor_audio, bass_audio]
        )
        
        cursor_btn.click(
            fn=update_cursor_position,
            inputs=[score_input, cursor_position],
            outputs=[score_image]
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
    print("🎼 Starting Choral Score Preview App...")
    
    # Check dependencies
    deps_status = {
        'Music21': MUSIC21_AVAILABLE,
        'FluidSynth': FLUIDSYNTH_AVAILABLE,
        'Matplotlib': MATPLOTLIB_AVAILABLE,
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
        print("  pip install music21 fluidsynth matplotlib scipy numpy")
        sys.exit(1)
    
    print("\n✅ All dependencies satisfied!")
    
    # Create and launch interface
    try:
        app = create_preview_interface()
        print("🚀 Launching at http://127.0.0.1:7862")
        
        app.launch(
            server_name="127.0.0.1",
            server_port=7862,  # Use different port to avoid conflicts
            share=False,
            debug=False
        )
    except Exception as e:
        print(f"\n❌ Failed to launch application: {e}")
        sys.exit(1)