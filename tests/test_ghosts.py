from core.score import load_musicxml
from core.editor.session import EditorSession
from core.llm.ghost_generator import generate_ghost_chords

score = load_musicxml("examples/test.xml")
session = EditorSession(score)

ghosts = generate_ghost_chords("Make romantic")
session.ghosts.clear()
for g in ghosts:
    session.ghosts.add(g)

assert len(session.ghosts.chords) > 0
print("Ghost-Chords Test OK")
