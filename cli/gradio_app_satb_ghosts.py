import gradio as gr

from core.score import load_musicxml, write_musicxml, replace_chord_in_measure
from core.editor.session import EditorSession
from core.llm.ghost_generator import generate_ghost_chords


def load_score(file):
    if file is None:
        return None, "Keine Datei ausgewählt."
    score = load_musicxml(file.name)
    session = EditorSession(score)
    return session, "Score geladen."


def run_llm(session, prompt):
    if session is None:
        return None, ["Keine Session aktiv."]
    # Ghosts erzeugen
    session.clear_ghosts()
    ghosts = generate_ghost_chords(prompt)
    for g in ghosts:
        session.ghosts.add(g)
    return session, session.ghosts.list_labels()


def accept_ghost(session, selected_index):
    if session is None or selected_index is None:
        return session, "Keine Auswahl / Session."
    try:
        ghost = session.ghosts.chords[int(selected_index)]
    except IndexError:
        return session, "Ungültiger Index."
    score = session.current_score
    replace_chord_in_measure(score, ghost.measure, ghost.root)
    session.apply(score)
    session.ghosts.chords.pop(int(selected_index))
    return session, f"Ghost Takt {ghost.measure} akzeptiert."


def reject_ghost(session, selected_index):
    if session is None or selected_index is None:
        return session, "Keine Auswahl / Session."
    try:
        ghost = session.ghosts.chords.pop(int(selected_index))
        return session, f"Ghost Takt {ghost.measure} verworfen."
    except IndexError:
        return session, "Ungültiger Index."


with gr.Blocks() as demo:
    gr.Markdown("## Ghost Chord Editor (LLM-Vorschläge)")

    # Gradio State korrekt initialisieren
    session_state = gr.State(value=None)

    file_in = gr.File(label="MusicXML")
    prompt = gr.Textbox(label="LLM Prompt")
    ghost_list = gr.Dropdown(label="Ghost Chords", choices=[], multiselect=False)

    status = gr.Textbox(label="Status")

    load_btn = gr.Button("Laden")
    llm_btn = gr.Button("LLM Vorschläge")
    accept_btn = gr.Button("Accept")
    reject_btn = gr.Button("Reject")

    # Callbacks
    load_btn.click(
        load_score,
        inputs=file_in,
        outputs=[session_state, status],
    )

    llm_btn.click(
        run_llm,
        inputs=[session_state, prompt],
        outputs=[session_state, ghost_list],
    )

    accept_btn.click(
        accept_ghost,
        inputs=[session_state, ghost_list],
        outputs=[session_state, status],
    )

    reject_btn.click(
        reject_ghost,
        inputs=[session_state, ghost_list],
        outputs=[session_state, status],
    )

demo.launch()
