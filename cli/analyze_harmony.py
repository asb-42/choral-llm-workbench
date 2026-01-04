import argparse
from core.score import load_musicxml
from core.score.harmony import analyze_chords


def main():
    parser = argparse.ArgumentParser(
        description="Analyze chords in a MusicXML score."
    )
    parser.add_argument("input", help="Input MusicXML file")
    args = parser.parse_args()

    score = load_musicxml(args.input)
    chords = analyze_chords(score)

    print("Harmonic analysis per measure:")
    for measure, chord_symbol in chords.items():
        print(f"  Measure {measure}: {chord_symbol}")


if __name__ == "__main__":
    main()
