import argparse
from core.score import load_musicxml, detect_voices


def main():
    parser = argparse.ArgumentParser(
        description="Analyze voices in a MusicXML score."
    )
    parser.add_argument("input", help="Input MusicXML file")
    args = parser.parse_args()

    score = load_musicxml(args.input)
    voices = detect_voices(score)

    print("Detected voices:")
    for part, voice in voices.items():
        print(f"  {part}: {voice}")


if __name__ == "__main__":
    main()
