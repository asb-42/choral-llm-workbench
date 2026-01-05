# File: cli/gradio_app_llm_models.py

import gradio as gr
import subprocess

# Dummy LLM für Testzwecke
class DummyLLM:
    def harmonize_prompt(self, prompt: str):
        # Gibt ein Mock-Ergebnis zurück
        return {"measure": 1, "root": "C", "quality": "major"}

# Globale Variable für das aktuell ausgewählte Modell
selected_llm = {"model": None, "name": None}

# Auswahlfunktion
def select_model(model_name: str):
    if model_name.lower() == "dummy":
        selected_llm["model"] = DummyLLM()
        selected_llm["name"] = "DummyModel"
    else:
        # Hier später reale Ollama-Integration
        selected_llm["model"] = DummyLLM()
        selected_llm["name"] = model_name
    return f"Selected LLM: {selected_llm['name']}"

# Harmonize-Funktion für SATB
def harmonize_voices(prompts):
    """
    Harmonize prompts for SATB voices.
    Accepts a dictionary {'S':..., 'A':..., 'T':..., 'B':...}.
    """
    if isinstance(prompts, dict):
        s_prompt = prompts.get("S", "")
        a_prompt = prompts.get("A", "")
        t_prompt = prompts.get("T", "")
        b_prompt = prompts.get("B", "")
    else:
        raise ValueError("Expected a dictionary with keys S,A,T,B")

    prompts_dict = {"S": s_prompt, "A": a_prompt, "T": t_prompt, "B": b_prompt}

    if selected_llm["model"] is None:
        return {}, "No LLM selected."

    results = {}
    for voice, prompt in prompts_dict.items():
        try:
            results[voice] = selected_llm["model"].harmonize_prompt(prompt)
        except Exception as e:
            results[voice] = f"Error: {str(e)}"
    
    return results, "Harmonization completed."

# Gradio UI
def launch_gradio_ui():
    with gr.Blocks() as demo:
        gr.Markdown("## SATB Harmonizer with LLM selection")

        with gr.Row():
            s_prompt = gr.Textbox(label="Soprano Prompt")
            a_prompt = gr.Textbox(label="Alto Prompt")
            t_prompt = gr.Textbox(label="Tenor Prompt")
            b_prompt = gr.Textbox(label="Bass Prompt")

        model_name = gr.Dropdown(["Dummy"], label="Select LLM")
        select_btn = gr.Button("Select Model")
        select_output = gr.Textbox(label="Model Selection")

        harmonize_btn = gr.Button("Harmonize")
        harmonize_output = gr.JSON(label="Harmonization Result")
        status = gr.Textbox(label="Status")

        # Callbacks
        select_btn.click(select_model, inputs=model_name, outputs=select_output)
        harmonize_btn.click(
            harmonize_voices,
            inputs=gr.State({
                "S": s_prompt,
                "A": a_prompt,
                "T": t_prompt,
                "B": b_prompt
            }),
            outputs=[harmonize_output, status]
        )

    demo.launch()

if __name__ == "__main__":
    launch_gradio_ui()
