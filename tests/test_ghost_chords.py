"""
Mini-Testscript für Ghost Chords (Schritt 13)
- lädt eine MusicXML-Datei
- erzeugt Ghost Chords über Dummy-LLM
- testet Accept / Reject
- prüft Session-Management
"""

from core.score import load_musicxml, replace_chord_in_measure
from core.editor.session import EditorSession
from core.llm.ghost_generator import generate_ghost_chords


def main():
    # 1️⃣ Score laden
    score_file = "examples/test.xml"
    score = load_musicxml(score_file)
    session = EditorSession(score)
    print("Score geladen.")

    # 2️⃣ Dummy LLM Ghosts erzeugen
    prompt = "Make measure 1 romantic"
    ghosts = generate_ghost_chords(prompt)
    for g in ghosts:
        session.ghosts.add(g)
    print(f"Ghosts erzeugt: {[g.label() for g in session.ghosts.chords]}")

    # 3️⃣ Accept Ghost Takt 1
    ghost_to_accept = session.ghosts.chords[0]
    replace_chord_in_measure(session.current_score, ghost_to_accept.measure, ghost_to_accept.root)
    session.apply(session.current_score)
    session.ghosts.chords.pop(0)
    print(f"Ghost akzeptiert: {ghost_to_accept.label()}")

    # 4️⃣ Reject Ghost Takt 2
    if len(session.ghosts.chords) > 0:
        ghost_to_reject = session.ghosts.chords[0]
        session.ghosts.chords.pop(0)
        print(f"Ghost verworfen: {ghost_to_reject.label()}")

    # 5️⃣ Final-Status prüfen
    print(f"Verbleibende Ghosts: {[g.label() for g in session.ghosts.chords]}")
    print(f"Session-Score Takte: {len(session.current_score.parts[0].getElementsByClass('Measure'))}")


if __name__ == "__main__":
    main()
