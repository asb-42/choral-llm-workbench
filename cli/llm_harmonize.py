import argparse
from llm.ollama_adapter import OllamaAdapter
from core.score import load_musicxml, detect_voices, analyze_chords

def main():
    parser = argparse.ArgumentParser(description="LLM-assisted harmony suggestion")
    parser.add_argument("input", help="Input MusicXML file")
    parser.add_argument("--prompt", required=True, help="Instruction for LLM (e.g., 'Make Takt 1 more romantic')")
    args = parser.parse_args()

    score = load_musicxml(args.input)
    voices = detect_voices(score)
    chords = analyze_chords(score)

    context = {
        "voices": voices,
        "chords": chords
    }

    llm = OllamaAdapter()
    suggestion = llm.generate_harmony(args.prompt, context)

    print("LLM Suggestion:")
    print(suggestion)

if __name__ == "__main__":
    main()
