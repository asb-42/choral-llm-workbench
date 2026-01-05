import gradio as gr

from core.score import load_musicxml, write_musicxml, replace_chord_in_measure
from core.editor.session import EditorSession


def load_score(path):
    score = load_musicxml(path)
    session = EditorSession(score)
    return session, "Score geladen."


def apply_edit(session, measure, root):
    if session is None:
        return None, "Keine Session aktiv."

    score = session.current_score
    replace_chord_in_measure(score, int(measure), root)
    session.apply(score)
    return session, f"Takt {measure} geändert."


def undo(session):
    if session is None:
        return None, "Keine Session aktiv."

    session.undo()
    return session, "Undo."


def redo(session):
    if session is None:
        return None, "Keine Session aktiv."

    session.redo()
    return session, "Redo."


def export_xml(session):
    if session is None:
        return None

    out = "output.xml"
    write_musicxml(session.current_score, out)
    return out


with gr.Blocks() as demo:
    gr.Markdown("## SATB Session Editor (Undo / Redo)")

    session_state = gr.State(None)

    file_in = gr.File(label="MusicXML")
    status = gr.Textbox(label="Status")

    measure = gr.Number(label="Takt", value=1)
    root = gr.Textbox(label="Akkordgrundton", value="C")

    load_btn = gr.Button("Laden")
    apply_btn = gr.Button("Anwenden")
    undo_btn = gr.Button("Undo")
    redo_btn = gr.Button("Redo")
    export_btn = gr.Button("Export MusicXML")

    file_out = gr.File(label="Export")

    load_btn.click(
        load_score,
        inputs=file_in,
        outputs=[session_state, status],
    )

    apply_btn.click(
        apply_edit,
        inputs=[session_state, measure, root],
        outputs=[session_state, status],
    )

    undo_btn.click(
        undo,
        inputs=session_state,
        outputs=[session_state, status],
    )

    redo_btn.click(
        redo,
        inputs=session_state,
        outputs=[session_state, status],
    )

    export_btn.click(
        export_xml,
        inputs=session_state,
        outputs=file_out,
    )

demo.launch()
