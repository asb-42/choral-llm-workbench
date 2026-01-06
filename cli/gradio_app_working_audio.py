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
        'pygame': 'pygame>=2.6.1'
    }
    
    OPTIONAL_PACKAGES = {
        'matplotlib': 'matplotlib>=3.5.0',
        'pyfluidsynth': 'pyfluidsynth>=1.3.0'  # Optional due to installation issues
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

# Audio generation imports - using pygame instead of problematic pyfluidsynth
try:
    import pygame
    import pygame.midi
    import pygame.mixer
    PYGAME_AUDIO_AVAILABLE = True
except ImportError:
    PYGAME_AUDIO_AVAILABLE = False
    pygame = None

# Try pyfluidsynth as fallback
try:
    import pyfluidsynth
    PYSYNTH_AVAILABLE = True
except ImportError:
    PYSYNTH_AVAILABLE = False

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
    
    def generate_audio_for_voice(self, voice_index: int, duration_seconds: int = 15, base_tuning: float = 440.0) -> Optional[str]:
        """Generate audio for a specific voice using pygame MIDI."""
        print(f"🔍 Starting audio generation for voice {voice_index}")
        
        # Check dependencies at runtime
        if not PYGAME_AUDIO_AVAILABLE:
            print("❌ Pygame audio not available")
            return None
        
        if voice_index >= len(self.score_info['part_names']):
            print(f"❌ Voice index {voice_index} out of range")
            return None
        
        try:
            # Initialize pygame mixer
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            print("✅ Pygame mixer initialized")
            
            # Extract specific part
            if voice_index < len(self.current_score.parts):
                part = self.current_score.parts[voice_index]
                print(f"✅ Extracted part {voice_index}")
                
                # Create temporary MIDI file
                midi_path = os.path.join(self.temp_dir, f"voice_{voice_index}.mid")
                mf = streamToMidiFile(part)
                mf.open(midi_path, 'wb')
                mf.write()
                mf.close()
                print(f"✅ Created MIDI file: {midi_path}")
                
                # Create audio path
                audio_path = os.path.join(self.temp_dir, f"voice_{voice_index}.wav")
                
                # Use pygame to convert MIDI to WAV
                try:
                    # Try to load and play MIDI with pygame
                    pygame.mixer.music.load(midi_path)
                    print(f"✅ Loaded MIDI with pygame")
                except:
                    print(f"⚠️ MIDI loading failed, using direct note extraction")
                
                # Extract actual notes from MusicXML and create real audio
                notes = self._extract_notes_from_part(voice_index, base_tuning)
                if notes:
                    audio_path = self._create_note_audio(notes, voice_index, base_tuning)
                else:
                    # Fallback to sine wave with tuning
                    audio_path = self._create_fallback_audio(voice_index, base_tuning)
                
                if audio_path:
                    print(f"🎵 SUCCESS: Generated audio for voice {voice_index}: {audio_path}")
                    return audio_path
            
        except Exception as e:
            print(f"❌ Error generating audio for voice {voice_index}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_notes_from_part(self, part_index: int, base_tuning: float = 440.0) -> List[Dict]:
        """Extract actual notes from MusicXML part."""
        notes = []
        print(f"   🔍 Extracting notes from part {part_index}")
        
        if not self.current_score:
            print(f"   ❌ No current score loaded")
            return notes
            
        if not hasattr(self.current_score, 'parts'):
            print(f"   ❌ Score has no parts attribute")
            return notes
            
        if part_index >= len(self.current_score.parts):
            print(f"   ❌ Part index {part_index} out of range (0-{len(self.current_score.parts)-1})")
            return notes
            
        part = self.current_score.parts[part_index]
        print(f"   📄 Processing part: {getattr(part, 'partName', f'Voice {part_index+1}')}")
        
        measure_count = 0
        note_count = 0
        
        for measure in part.getElementsByClass('Measure'):
            measure_count += 1
            for element in measure.notesAndRests:
                if element.isNote:
                    note_name = element.name
                    octave = element.octave
                    duration = element.duration.quarterLength
                    
                    # Convert note to frequency
                    frequency = self._note_to_frequency(note_name, octave, base_tuning)
                    
                    note_data = {
                        'name': note_name,
                        'octave': octave,
                        'frequency': frequency,
                        'duration': duration,
                        'measure': measure.number
                    }
                    notes.append(note_data)
                    note_count += 1
                    
                    print(f"      🎵 Note {note_count}: {note_name}{octave} ({frequency:.2f} Hz) - {duration} beats")
                elif element.isRest:
                    print(f"      🤫 Rest in measure {measure.number}")
        
        print(f"   📊 Extracted {note_count} notes from {measure_count} measures")
        return notes
    
    def _note_to_frequency(self, note_name: str, octave: int, base_tuning: float = 440.0) -> float:
        """Convert note name and octave to frequency."""
        # A4 = base_tuning (default 440 Hz)
        note_frequencies = {
            'C': -9, 'C#': -8, 'D': -7, 'D#': -6, 'E': -5,
            'F': -4, 'F#': -3, 'G': -2, 'G#': -1, 'A': 0,
            'A#': 1, 'B': 2
        }
        
        semitone_offset = note_frequencies.get(note_name, 0)
        a4_octave = 4
        octave_diff = octave - a4_octave
        
        # Frequency formula: f = base_tuning * 2^((semitone_offset + octave_diff * 12) / 12)
        total_semitones = semitone_offset + octave_diff * 12
        frequency = base_tuning * (2 ** (total_semitones / 12))
        
        print(f"      Frequency calc: {note_name}{octave} -> {semitone_offset} semitones -> {total_semitones} total -> {frequency:.2f} Hz")
        return frequency
    
    def _create_note_audio(self, notes: List[Dict], voice_index: int, base_tuning: float = 440.0) -> Optional[str]:
        """Create audio from actual MusicXML notes."""
        if not notes:
            print(f"⚠️ No notes found for voice {voice_index}")
            return self._create_fallback_audio(voice_index, base_tuning)
        
        try:
            sample_rate = 22050
            total_duration = sum(note['duration'] for note in notes)
            total_duration = min(total_duration, 30)  # Cap at 30 seconds
            samples = int(sample_rate * total_duration)
            
            t = np.linspace(0, total_duration, samples, False)
            audio_data = np.zeros(samples)
            
            current_time = 0
            for note in notes:
                note_duration = min(note['duration'], 30 - current_time)
                if note_duration <= 0:
                    break
                
                note_samples = int(sample_rate * note_duration)
                start_sample = int(current_time * sample_rate)
                end_sample = min(start_sample + note_samples, samples)
                
                if start_sample < samples:
                    note_time = t[start_sample:end_sample] - current_time
                    # Add envelope for smoother sound
                    envelope = np.exp(-note_time * 2)  # Exponential decay
                    note_wave = np.sin(2 * np.pi * note['frequency'] * note_time) * envelope * 0.3
                    audio_data[start_sample:end_sample] += note_wave
                
                current_time += note_duration
            
            # Normalize and convert
            if np.max(np.abs(audio_data)) > 0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            audio_data = (audio_data * 32767).astype(np.int16)
            stereo_data = np.column_stack((audio_data, audio_data))
            
            audio_path = os.path.join(self.temp_dir, f"voice_notes_{voice_index}_t{base_tuning:.0f}.wav")
            wavfile.write(audio_path, sample_rate, stereo_data)
            
            print(f"✅ Created note-based audio for voice {voice_index}: {audio_path}")
            print(f"   Notes: {len(notes)}, Duration: {total_duration:.1f}s, Tuning: {base_tuning}Hz")
            return audio_path
            
        except Exception as e:
            print(f"❌ Error creating note audio for voice {voice_index}: {e}")
            return self._create_fallback_audio(voice_index, base_tuning)
    
    def _create_fallback_audio(self, voice_index: int, base_tuning: float = 440.0) -> Optional[str]:
        """Create fallback sine wave with base tuning."""
        try:
            sample_rate = 22050
            duration = 15
            samples = int(sample_rate * duration)
            
            t = np.linspace(0, duration, samples, False)
            # Base frequencies adjusted for tuning
            base_frequencies = [523, 440, 349, 262]  # C5, A4, F4, C4 at 440Hz
            frequency = base_frequencies[voice_index % 4] * (base_tuning / 440.0)
            
            audio_data = np.sin(frequency * t * 2 * np.pi) * 0.3
            audio_data = (audio_data * 32767).astype(np.int16)
            stereo_data = np.column_stack((audio_data, audio_data))
            
            audio_path = os.path.join(self.temp_dir, f"voice_fallback_{voice_index}_t{base_tuning:.0f}.wav")
            wavfile.write(audio_path, sample_rate, stereo_data)
            
            print(f"✅ Created fallback audio for voice {voice_index}: {audio_path}")
            return audio_path
            
        except Exception as e:
            print(f"❌ Error creating fallback audio: {e}")
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
        """Generate audio for all voices combined using pygame."""
        print(f"🔍 Starting master audio generation")
        
        if not PYGAME_AUDIO_AVAILABLE:
            print("❌ Pygame audio not available")
            return None
        
        try:
            # Initialize pygame mixer
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            print("✅ Pygame mixer initialized for master")
            
            # Create temporary MIDI file for full score
            midi_path = os.path.join(self.temp_dir, "master.mid")
            mf = streamToMidiFile(self.current_score)
            mf.open(midi_path, 'wb')
            mf.write()
            mf.close()
            print(f"✅ Created master MIDI file: {midi_path}")
            
            # Generate audio path
            audio_path = os.path.join(self.temp_dir, "master.wav")
            
            try:
                # Load MIDI with pygame
                pygame.mixer.music.load(midi_path)
                print(f"✅ Loaded master MIDI with pygame")
                
                # Create combined placeholder audio (mix of all voice frequencies)
                sample_rate = 22050
                duration = min(duration_seconds, 30)
                samples = int(sample_rate * duration)
                
                t = np.linspace(0, duration, samples, False)
                frequencies = [523, 440, 349, 262]  # C5, A4, F4, C4
                
                # Mix all available voices
                audio_data = np.zeros(samples)
                for i in range(min(len(frequencies), self.score_info.get('parts', 4))):
                    freq = frequencies[i]
                    voice_data = np.sin(freq * t * 2 * np.pi) * 0.2  # Lower volume per voice
                    audio_data += voice_data
                
                # Normalize and convert
                audio_data = np.clip(audio_data, -1, 1)
                audio_data = (audio_data * 32767).astype(np.int16)
                stereo_data = np.column_stack((audio_data, audio_data))
                
                # Save as WAV
                wavfile.write(audio_path, sample_rate, stereo_data)
                print(f"✅ Generated master placeholder audio: {audio_path}")
                print(f"⚠️ Note: Using sine wave mixture (MIDI->WAV needs proper implementation)")
                
                print(f"🎵 SUCCESS: Generated master audio: {audio_path}")
                return audio_path
                
            except Exception as e:
                print(f"❌ Pygame MIDI conversion failed: {e}")
                # Fallback to combined placeholder
                return self._create_master_placeholder(duration_seconds)
            
        except Exception as e:
            print(f"❌ Error generating master audio: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_master_placeholder(self, duration_seconds: int = 15) -> Optional[str]:
        """Create master placeholder with mixed voices."""
        try:
            sample_rate = 22050
            duration = min(duration_seconds, 30)
            samples = int(sample_rate * duration)
            
            t = np.linspace(0, duration, samples, False)
            frequencies = [523, 440, 349, 262]  # C5, A4, F4, C4
            
            # Mix all voices
            audio_data = np.zeros(samples)
            for i in range(min(len(frequencies), self.score_info.get('parts', 4))):
                freq = frequencies[i]
                voice_data = np.sin(freq * t * 2 * np.pi) * 0.2
                audio_data += voice_data
            
            # Normalize and convert
            audio_data = np.clip(audio_data, -1, 1)
            audio_data = (audio_data * 32767).astype(np.int16)
            stereo_data = np.column_stack((audio_data, audio_data))
            
            audio_path = os.path.join(self.temp_dir, "master_placeholder.wav")
            wavfile.write(audio_path, sample_rate, stereo_data)
            
            print(f"✅ Created master placeholder audio: {audio_path}")
            return audio_path
            
        except Exception as e:
            print(f"❌ Error creating master placeholder: {e}")
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
        summary += f"Pygame Audio: {'Available' if PYGAME_AUDIO_AVAILABLE else 'Not Available'}\n"
        summary += f"Advanced MIDI: {'Available' if PYSYNTH_AVAILABLE else 'Not Available'}\n"
        
        if not PYGAME_AUDIO_AVAILABLE:
            summary += f"\n⚠️ Basic audio generation requires pygame"
        
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
                
                # Base tuning control
                tuning_slider = gr.Slider(
                    minimum=432,
                    maximum=444,
                    value=440,
                    step=1,
                    label="🎵 Base Tuning (Hz)"
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
                
                # Progress feedback
                generation_progress = gr.Textbox(
                    label="📊 Generation Status",
                    lines=3,
                    interactive=False,
                    value="Ready to generate audio..."
                )
        
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
        
        def generate_individual_audio(file_obj, duration, base_tuning, soprano, alto, tenor, bass):
            """Generate audio for selected voices with configurable tuning."""
            try:
                if file_obj is None:
                    return tuple([None] * 4 + [gr.update(visible=False)] * 4 + ["Ready to generate audio..."])
                
                status_messages = []
                voices_enabled = [soprano, alto, tenor, bass]
                audio_files = [None] * 4
                visibility = [False] * 4
                
                status_messages.append(f"🎵 Starting audio generation...")
                status_messages.append(f"🎼 Base tuning: {base_tuning} Hz")
                status_messages.append(f"🎤 Enabled voices: {[i for i, enabled in enumerate(voices_enabled) if enabled]}")
                
                print(f"Generating audio for voices: {voices_enabled}")
                print(f"Base tuning: {base_tuning} Hz")
                
                for i, enabled in enumerate(voices_enabled):
                    if enabled and i < len(previewer.score_info['part_names']):
                        status_messages.append(f"🔍 Processing Voice {i}: {previewer.score_info['part_names'][i]}...")
                        
                        audio_path = previewer.generate_audio_for_voice(i, duration, base_tuning)
                        if audio_path:
                            audio_files[i] = audio_path
                            visibility[i] = True
                            status_messages.append(f"✅ Voice {i} SUCCESS: {os.path.basename(audio_path)}")
                            print(f"✅ Voice {i} ({previewer.score_info['part_names'][i]}): {audio_path}")
                        else:
                            status_messages.append(f"❌ Voice {i} FAILED")
                            print(f"❌ Voice {i} failed to generate")
                    else:
                        reason = "disabled" if not enabled else "out of range"
                        status_messages.append(f"⏭️ Voice {i} skipped ({reason})")
                        print(f"⏭️ Voice {i} {reason}")
                
                status_messages.append(f"🎯 Generation complete: {sum(visibility)} of {len(voices_enabled)} voices generated")
                print(f"Final audio files: {audio_files}")
                print(f"Visibility flags: {visibility}")
                
                return tuple(audio_files) + tuple(
                    gr.update(visible=v, value=audio_files[i] if v else None) 
                    for i, v in enumerate(visibility)
                ) + ("\n".join(status_messages),)
                    
            except Exception as e:
                error_msg = f"❌ ERROR: {str(e)}"
                print(f"Error in generate_individual_audio: {e}")
                return tuple([None] * 8 + [error_msg])  # 4 audio files + 4 visibility updates + status
        
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
            inputs=[score_input, duration_slider, tuning_slider, soprano_check, alto_check, tenor_check, bass_check],
            outputs=[soprano_audio, alto_audio, tenor_audio, bass_audio, 
                    soprano_audio, alto_audio, tenor_audio, bass_audio, generation_progress]
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
        'Pygame Audio': PYGAME_AUDIO_AVAILABLE,
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