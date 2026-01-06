#!/usr/bin/env python3
import argparse, json, os, sys, base64
from pathlib import Path
from music21 import converter, stream


def render_voice_audio_from_score(score_path: str, voice: str, tuning: float, duration: float, soundfont: str, outdir: str):
    score = converter.parse(score_path)
    voice_index = {'S': 0, 'A': 1, 'T': 2, 'B': 3}.get(voice, 0)
    voice_part = score.parts[voice_index] if voice_index < len(score.parts) else None
    if voice_part is None:
        return None
    new_score = stream.Score()
    new_score.append(voice_part)
    midi_path = os.path.join(outdir, f"{voice}.mid")
    new_score.write('midi', midi_path)
    wav_path = os.path.join(outdir, f"{voice}.wav")
    try:
        cmd = ["fluidsynth", "-T", "wav", "-n", "-F", wav_path, midi_path, soundfont]
        import subprocess
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        return None
    if os.path.exists(wav_path):
        with open(wav_path, 'rb') as f:
            data = f.read()
        b64 = base64.b64encode(data).decode('ascii')
        src = f"data:audio/wav;base64,{b64}"
        return {"voice": voice, "src": src, "label": voice}
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--score-path', required=True)
    parser.add_argument('--voices', required=True)
    parser.add_argument('--tuning', type=float, default=432)
    parser.add_argument('--duration', type=float, default=0.8)
    parser.add_argument('--soundfont', default='~/.fluidsynth/default_sound_font.sf2')
    parser.add_argument('--outdir', default='storage/voices')
    args = parser.parse_args()
    voices = [v.strip() for v in args.voices.split(',') if v.strip()]
    outdir = args.outdir
    Path(outdir).mkdir(parents=True, exist_ok=True)
    results = []
    for v in voices:
        r = render_voice_audio_from_score(args.score_path, v, args.tuning, args.duration, args.soundfont, outdir)
        if r:
            results.append(r)
    print(json.dumps({"perVoiceAudios": results}))

if __name__ == '__main__':
    main()
