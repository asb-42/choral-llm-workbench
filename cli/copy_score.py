import argparse
from core.score import load_musicxml, write_musicxml


def main():
    parser = argparse.ArgumentParser(
        description="Load a MusicXML file and write it back unchanged."
    )
    parser.add_argument("input", help="Input MusicXML file")
    parser.add_argument("output", help="Output MusicXML file")

    args = parser.parse_args()

    print(f"Loading score from {args.input}...")
    score = load_musicxml(args.input)

    print(f"Writing score to {args.output}...")
    write_musicxml(score, args.output)

    print("Done.")


if __name__ == "__main__":
    main()
