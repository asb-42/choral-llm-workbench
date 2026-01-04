import argparse
from core.score import load_musicxml, write_musicxml
from core.score.reharmonize import replace_chord_in_measure
from llm.ollama_adapter import OllamaAdapter

def main():
    parser = argparse.ArgumentParser(
        description="LLM-assisted reharmonization of a single measure"
    )
    parser.add_argument("input", help="Input MusicXML file")
    parser.add_argument("output", help="Output MusicXML file")
    parser.add_argument("--measure", type=int, required=True, help="Measure number to modify")
    parser.add_argument("--prompt", required=True, help="Instruction for LLM")
    args = parser.parse_args()

    score = load_musicxml(args.input)

    # Analyse vorbereiten
    llm = OllamaAdapter()
    context = {}  # optional: Stimmen / Akkorde können hier eingefügt werden
    suggestion = llm.generate_harmony(args.prompt, context)

    # MVP: wir nehmen nur den Root der vorgeschlagenen Akkordwurzel
    # z.B. aus dem LLM-Text "Use C major" → extrahieren wir "C"
    # Für MVP einfach: Benutzer schreibt Root in Prompt
    root_note = args.prompt.strip().split()[-1]  # letzte Wort als Root

    replace_chord_in_measure(score, args.measure, root_note)
    write_musicxml(score, args.output)

    print(f"Measure {args.measure} reharmonized with LLM suggestion '{root_note}' in {args.output}")

if __name__ == "__main__":
    main()
