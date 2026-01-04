import argparse
from core.score import load_musicxml, write_musicxml
from core.score.reharmonize import replace_chord_in_measure

def main():
    parser = argparse.ArgumentParser(
        description="Reharmonize a single measure in a MusicXML score."
    )
    parser.add_argument("input", help="Input MusicXML file")
    parser.add_argument("output", help="Output MusicXML file")
    parser.add_argument("--measure", type=int, required=True, help="Measure number to modify")
    parser.add_argument("--root", required=True, help="New root note (e.g., C, F, G)")
    args = parser.parse_args()

    score = load_musicxml(args.input)
    replace_chord_in_measure(score, args.measure, args.root)
    write_musicxml(score, args.output)
    print(f"Measure {args.measure} replaced with {args.root} triad in {args.output}.")

if __name__ == "__main__":
    main()
