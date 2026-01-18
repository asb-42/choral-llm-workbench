# Choral Music Transformer

**Deterministic choral music transformation engine** built on MusicXML and LLM technology.  
Designed for professional choir conductors, arrangers, and composers.

This tool enables:

- **Polyphonic transformations**: SATB and additional accompaniment voices supported
- **Complex rhythm handling**: irregular meters, polyrhythms, and precise note durations
- **Harmonic reharmonization**: explicit harmony events with key context
- **Transposition & style adaptation**: controlled, deterministic changes for professional workflows
- **LLM-assisted workflow**: text-based representation (TLR) ensures explainability and reproducibility
- **Roundtrip MusicXML support**: maintain original structure and musical correctness

**Target Users:** Choir directors, arrangers, and composers who need deterministic, AI-assisted transformations while retaining full musical control.

---

## 📖 Documentation

For detailed installation, usage instructions, and examples, please see the **[User Manual (USER_MANUAL.md)](USER_MANUAL.md)**.

## Quick Overview

The **Choral Music Transformer** is a production-ready framework for deterministic choral music transformation. It combines traditional MusicXML representation with AI-driven transformations while maintaining strict musical correctness and professional workflow compatibility.

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


## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd choral-llm-workbench
   ```

2. **Set up the environment** (see [User Manual](USER_MANUAL.md) for detailed instructions):
   ```bash
   python -m venv .venv
   source .venv/bin/activate       # Linux/macOS
   # or .venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```

3. **Launch the application:**
   ```bash
   python app.py
   ```

4. **Open browser:** `http://localhost:7860`

## System Requirements

- **Python**: 3.11+ with type hints
- **RAM**: 8GB+ recommended for LLM operations
- **Browser**: Modern web browser with HTML5 support
- **Optional**: Local LLM (Ollama or compatible service)

## Key Dependencies

- `gradio` - Web UI framework
- `music21` - Music notation and analysis
- `pygame`, `pyfluidsynth` - Audio rendering
- **Optional**: SoundFont for MIDI/WAV output

## Installation Methods

### Standard Installation
Follow the detailed setup in the [User Manual](USER_MANUAL.md).

### Pinokio Installation
```bash
bash install_pinokio.sh
```

### Audio Setup
For audio rendering, install a SoundFont:
- Path: `~/.fluidsynth/default_sound_font.sf2`
- Recommended: [FluidR3_GM.sf2](https://member.keymusician.com/Member/FluidR3_GM/index.html)

## Legacy CLI Interfaces

Legacy Gradio apps are available in the `cli/` directory:
```bash
python cli/gradio_app_satb_llm.py
```



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
