import json
from core.editor.session import EditorSession
from core.score.parser import load_musicxml
from cli.gradio_app_satb_llm import DummyLLM, harmonize_multi_voice

def main():
    # Testscore laden
    score_file = "examples/test.xml"
    session = EditorSession()
    
    # Multi-Voice Prompts
    prompts_json = json.dumps({
        "S": "bright",
        "A": "passing tone",
        "T": "romantic",
        "B": "stable"
    })
    
    out_file, out_audio, log = harmonize_multi_voice(open(score_file, "rb"), prompts_json)
    
    print("Log:", log)
    print("Updated Score File:", out_file)
    print("Audio Preview File:", out_audio)

if __name__ == "__main__":
    main()
