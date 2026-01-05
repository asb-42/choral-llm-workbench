from core.editor.ghost import GhostChord


def generate_ghost_chords(prompt: str):
    """
    Platzhalter für LLM-Ausgabe.
    Später: Parsing echter LLM-Antworten.
    """
    ghosts = []

    if "romantic" in prompt.lower():
        ghosts.append(GhostChord(measure=1, root="Am"))
        ghosts.append(GhostChord(measure=2, root="F"))

    return ghosts
