# Getting Started with Choral LLM Workbench

This guide provides a quick introduction to loading, harmonizing, and previewing choral scores using the **Choral LLM Workbench**.

---

## Prerequisites

- Python 3.12+
- Virtual environment (`venv`) or Conda
- Dependencies installed via `requirements.txt`
- Example MusicXML files (e.g., `examples/test.xml`)

---

## Setup

1. **Clone the repository and navigate into it**

git clone <repository_url>
cd choral-llm-workbench


## Create and activate a virtual environment

python -m venv .venv
source .venv/bin/activate       # Linux/macOS
.venv\Scripts\activate          # Windows


## Install Python dependencies

pip install -r requirements.txt


## Running a Gradio SATB LLM Interface

python cli/gradio_app_satb_llm.py


Open the local URL (usually http://127.0.0.1:7860) in your browser.

Upload a MusicXML score.

Enter prompts for Soprano, Alto, Tenor, and Bass voices (e.g., Make measure 1 more romantic).

Click Harmonize to apply the LLM-based suggestions.

Preview the harmonized score as MIDI or WAV.

## Testing with Dummy LLM

For initial testing without a real AI backend, a Dummy LLM is included:

from core.editor.dummy_llm import DummyLLM

llm = DummyLLM()
prompts = {
    "S": "C major",
    "A": "G major",
    "T": "E minor",
    "B": "C major"
}

result = llm.harmonize_multi_voice(prompts)
print(result)

This returns a dictionary of suggested chords per voice.

## Reharmonization and Measure Editing

You can replace chords in a specific measure using the CLI:

python cli/analyze_harmony.py examples/test.xml
python cli/llm_harmonize.py examples/test.xml --prompt "Make measure 1 more romantic"


Use replace_chord_in_measure(score, measure, root) in scripts for programmatic editing.


## Audio Preview

MIDI/WAV previews are supported in the Gradio interface.

Requires a working SoundFont (.sf2) if using WAV rendering.

For MIDI preview, standard MIDI synthesizers are used.


## Notes

The current setup uses a Dummy LLM; real AI LLMs can be integrated via core/editor/llm.py.

All input scores must be valid MusicXML files (.xml or .mxl).

Error messages will be displayed in the Gradio app if prompts or scores are invalid.


## Example Files

You can find example scores in:

examples/test.xml
examples/Bach_Joy_of_Man_Desiring.mxl



## Next Steps

Experiment with different prompts per voice.

Test audio previews.

Integrate real LLM backends for automated harmonization.

Explore session-based editing in core/editor/session.py.
