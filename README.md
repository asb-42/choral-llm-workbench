# Choral LLM Workbench

## Overview

The **Choral LLM Workbench** is an experimental framework for exploring AI-assisted choral composition and harmony analysis. Its goal is to allow musicians, composers, and researchers to interactively harmonize, edit, and explore SATB (Soprano, Alto, Tenor, Bass) choral music using modular AI language models (LLMs) while maintaining fine-grained control over musical structures.

The workbench combines traditional music representation via **MusicXML** with AI-driven harmonization, reharmonization, and chord analysis.

---

## Key Features

1. **Score Loading and Analysis**  
   - Load choral scores in MusicXML format.
   - Analyze existing harmony using music21.
   - Detect voice parts and chord structures.

2. **AI-Assisted Harmonization**  
   - Harmonize individual measures or entire SATB scores using pluggable LLMs.  
   - Supports multi-prompt input per voice (S, A, T, B).  
   - Uses a modular LLM interface; currently, a **Dummy LLM** is included for testing.

3. **Interactive Editing**  
   - Apply and undo changes to individual measures.
   - Maintain session history and score state.

4. **Ghost Chords / Suggestions**  
   - Generate alternative chord suggestions for measures.
   - Accept or reject suggested chords interactively.

5. **Audio Preview**  
   - Render MIDI or WAV audio previews of the harmonized score.
   - Supports multiple output formats for immediate listening.

6. **Gradio-Based GUI**  
   - Browser-based interfaces for interactive harmonization, multi-voice prompts, and measure editing.
   - Real-time feedback and audio preview capabilities.


## Installation Requirements

- Python 3.12
- Packages (install via `pip install -r requirements.txt`):
  - `gradio`
  - `music21`
  - `pygame`
  - `mido`
  - `anyio`
- A **General MIDI SoundFont** for audio rendering:
  - Path: `~/.fluidsynth/default_sound_font.sf2`
  - Recommended: [FluidR3_GM.sf2](https://member.keymusician.com/Member/FluidR3_GM/index.html)
- Optional audio tunings supported: **432 Hz, 440 Hz, 443 Hz**.


## Getting Started

1. Clone the repository:

git clone <repository_url>
cd choral-llm-workbench

2. Create and activate a Python virtual environment:

python -m venv .venv
source .venv/bin/activate       # Linux/macOS
.venv\Scripts\activate          # Windows

3. Install dependencies:

pip install -r requirements.txt

4. Download a default SoundFont to ~/.fluidsynth/default_sound_font.sf2

Alternatively if you want to use Pinokio:

Run the installation script:

bash install_pinokio.sh


5. Activate the virtual environment:

source .venv/bin/activate

6. Run an example Gradio interface:

python cli/gradio_app_satb_llm.py



## Usage Notes

Currently, a Dummy LLM is included for testing; real LLM models can be integrated via Ollama or other pluggable backends.

All scores must be in MusicXML format. .mxl compressed MusicXML is supported.

Audio previews require a working MIDI synthesizer or SoundFont.


## Configuration

The application reads global settings from `core/config.py`:


# Base tuning for audio preview in Hz
BASE_TUNING = 432.0


## Testing Audio Rendering

A dedicated test script is provided to verify WAV rendering:

python tests/test_gradio_audio_wav.py

This script

- Loads a test MusicXML score.
- Generates a temporary MIDI file.
- Converts it to WAV files at 432 Hz, 440 Hz, and 443 Hz.
- Requires a valid SoundFont in ~/.fluidsynth/default_sound_font.sf2.


## Directory Structure

./cli/               # Gradio app entry points
./core/              # Core logic (score handling, audio, dummy LLM)
./tests/             # Unit and integration tests
./docs/              # Documentation (this README.md)



## Goals and Future Work

Integrate real AI LLMs for harmonization and multi-voice composition.

Expand music theory analysis (advanced chord, modulation, voice leading).

Improve error handling and user feedback in Gradio interfaces.

Support collaborative session management and undo/redo across multiple edits.


##License

This project is licensed under the MIT License. See LICENSE for details.
