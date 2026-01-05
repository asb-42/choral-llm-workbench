from core.editor.session import EditorSession
from core.score.parser import load_musicxml

def main():
    session = EditorSession()
    score = load_musicxml("examples/test.xml")
    session.load_score(score)

    print("Original Score geladen")

    # Simuliere Bearbeitung
    from core.score.reharmonize import replace_chord_in_measure
    replace_chord_in_measure(session.current_score, 1, "Am")
    session.apply_edit(session.current_score)
    print("Änderung 1 angewendet")

    # Undo
    session.undo()
    print("Undo durchgeführt")

    # Redo
    session.redo()
    print("Redo durchgeführt")

if __name__ == "__main__":
    main()
