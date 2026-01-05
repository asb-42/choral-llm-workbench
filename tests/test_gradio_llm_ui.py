# File: tests/test_gradio_llm_ui.py

import gradio as gr
from cli.gradio_app_llm_models import select_model, harmonize_voices

def run_gradio_test():
    # Dummy-LLM auswählen
    select_model("Dummy")

    def harmonize_interface(s_prompt, a_prompt, t_prompt, b_prompt):
        prompts = {
            "S": s_prompt,
            "A": a_prompt,
            "T": t_prompt,
            "B": b_prompt
        }
        results, status = harmonize_voices(prompts)
        return results, status

    # Gradio Interface
    with gr.Blocks() as demo:
        gr.Markdown("### SATB Harmonization Test (Dummy LLM)")

        s_input = gr.Textbox(label="Soprano prompt", value="Make soprano lyrical")
        a_input = gr.Textbox(label="Alto prompt", value="Smooth alto line")
        t_input = gr.Textbox(label="Tenor prompt", value="Add warmth to tenor")
        b_input = gr.Textbox(label="Bass prompt", value="Strengthen bass foundation")

        output_text = gr.Textbox(label="Harmonization Results")
        status_text = gr.Textbox(label="Status")

        run_btn = gr.Button("Harmonize")
        run_btn.click(
            harmonize_interface,
            inputs=[s_input, a_input, t_input, b_input],
            outputs=[output_text, status_text]
        )

    demo.launch(share=False)

if __name__ == "__main__":
    run_gradio_test()
