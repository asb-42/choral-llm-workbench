from core.editor.session import EditorSession
from core.score.parser import load_musicxml
from core.llm.satb import SATBLLM

# Dummy LLM für Tests
class DummyLLM:
    def generate_chord(self, prompt):
        # Sehr einfache Simulation: gibt immer Am zurück
        return {"root": "A", "quality": "minor"}

def main():
    session = EditorSession()
    score = load_musicxml("examples/test.xml")
    session.load_score(score)

    llm = DummyLLM()
    satb_llm = SATBLLM(session, llm)

    chord_name = satb_llm.harmonize_prompt(1, "Make measure 1 more romantic")
    print(f"Takt 1 harmonisiert zu: {chord_name}")

if __name__ == "__main__":
    main()
