#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def patch_file(path: str) -> bool:
    p = Path(path)
    if not p.exists():
        print(f"Patch: file not found: {path}")
        return False
    content = None
    try:
        with p.open('r', encoding='utf-8') as f:
            content = f.read()
        data = json.loads(content)
    except Exception:
        # Try a lax salvage: remove musicxml-json text occurrences
        new_content = content if content is not None else ''
        new_content = new_content.replace('"musicxml-json":', '')
        try:
            data = json.loads(new_content)
            content = new_content
        except Exception as e:
            print(f"Patch: could not parse {path}: {e}")
            return False
    if isinstance(data, dict):
        changed = False
        for key in ('dependencies','devDependencies'):
            if key in data and isinstance(data[key], dict):
                if 'musicxml-json' in data[key]:
                    del data[key]['musicxml-json']
                    changed = True
        if changed:
            with p.open('w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"Patched {path}")
            return True
    print(f"No patch needed for {path}")
    return False

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        patch_file(arg)
