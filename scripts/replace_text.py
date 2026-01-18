#!/usr/bin/env python3
import argparse
from pathlib import Path

def replace_in_file(path: Path, old: str, new: str):
    if not path.exists():
        print(f"skip missing {path}")
        return
    text = path.read_text(encoding='utf-8')
    if old not in text:
        return
    text = text.replace(old, new)
    path.write_text(text, encoding='utf-8')
    print(f"patched {path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pattern', required=True, help='text to replace')
    parser.add_argument('--replacement', required=True, help='replacement text')
    parser.add_argument('--files', nargs='+', required=True, help='files to patch')
    args = parser.parse_args()
    for f in args.files:
        path = Path(f)
        replace_in_file(path, args.pattern, args.replacement)

if __name__ == '__main__':
    main()
