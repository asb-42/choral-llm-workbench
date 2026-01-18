import gradio as gr
import os
import tempfile
from typing import Tuple, Optional
from musicxml_parser import MusicXMLParser
from tlr_converter import TLRConverter
from tlr_parser import TLRParser
from ollama_llm import OllamaLLM
from musicxml_exporter import MusicXMLExporter
from helmholtz_converter import HelmholtzConverter
from explainer_llm import ExplainerLLM
from event_indexer import EventIndexer
from transformation_validator import TransformationValidator
from tlr_diff_viewer import TLTDiffViewer


class ChoralWorkbench:
    """Main application class for the Choral LLM Workbench"""
    
    def __init__(self):
        self.parser = MusicXMLParser()
        self.tlr_converter = TLRConverter()
        self.tlr_parser = TLRParser()
        self.llm = OllamaLLM()
        self.exporter = MusicXMLExporter()
        self.helmholtz_converter = HelmholtzConverter()
        self.explainer_llm = ExplainerLLM()
        self.event_indexer = EventIndexer()
        self.transformation_validator = TransformationValidator()
        self.diff_viewer = TLTDiffViewer()
        
        # Initialize Ollama models
        self.available_models = []
        if self.llm.check_connection():
            try:
                self.available_models = self.llm.get_available_models()
            except Exception:
                self.available_models = []
        
        # State
        self.current_score = None
        self.original_score = None  # For explanation mode
        self.original_tlr = None  # For diff view
        self.current_tlr = None
        self.output_file = None
        self.current_notation = "spn"  # "spn" or "helmholtz"
        self.current_mode = "transform"  # "transform" or "explain"
        self.transformation_flags = set()  # Active transformation flags
    
    def upload_and_parse(self, file_obj) -> Tuple[str, str]:
        """Upload MusicXML file and convert to TLR"""
        if file_obj is None:
            return "", "Please upload a MusicXML file."
        
        try:
            # Parse MusicXML
            self.current_score = self.parser.parse(file_obj.name)
            
            # Store original TLR for diff
            if self.current_score:
                self.original_tlr = self.tlr_converter.ikr_to_tlr(self.current_score)
            
            # Convert to appropriate notation based on current setting
            tlr_display = self._get_current_notation_display()
            
            return tlr_display, "Successfully parsed MusicXML file."
            
        except Exception as e:
            return "", f"Error parsing file: {str(e)}"
    
    def _get_current_notation_display(self) -> str:
        """Get current notation display based on setting"""
        if self.current_score is None:
            return ""
        
        if self.current_notation == "helmholtz":
            return self.helmholtz_converter.score_to_helmholtz_tlr(self.current_score)
        else:
            return self.tlr_converter.ikr_to_tlr(self.current_score)
    
    def switch_notation(self, notation_choice: str) -> str:
        """Switch between SPN and Helmholtz notation"""
        self.current_notation = notation_choice
        return self._get_current_notation_display()
    
    def switch_mode(self, mode_choice: str) -> Tuple[str, str, str]:
        """Switch between transform and explain mode"""
        self.current_mode = mode_choice
        
        if mode_choice == "explain":
            # In explain mode, show event summary and explanation interface
            if self.current_score:
                event_summary = self.explainer_llm.get_event_summary(self.current_score)
                return "", "EXPLANATION MODE - Read Only Analysis", event_summary
            else:
                return "", "EXPLANATION MODE - Please upload a MusicXML file first", ""
        else:
            # Transform mode - show current TLR
            tlr_display = self._get_current_notation_display()
            return tlr_display, "TRANSFORMATION MODE - Edit and Transform Music", ""
    
    def explain_music(self, question: str) -> str:
        """Answer user question about current music"""
        if not question.strip():
            return "Please enter a question about the music."
        
        if self.current_mode != "explain":
            return "Please switch to explanation mode first."
        
        if not self.current_score:
            return "Please upload a MusicXML file first."
        
        try:
            # Get explanation based on whether we have a transformed version
            if self.original_score and self.original_score != self.current_score:
                # Explain transformation
                explanation, errors = self.explainer_llm.explain_transformation(
                    self.original_score, self.current_score, question
                )
            else:
                # Explain context
                explanation, errors = self.explainer_llm.explain_score_context(
                    self.current_score, question
                )
            
            if errors:
                return f"Analysis errors: {'; '.join(errors)}"
            
            return explanation
            
        except Exception as e:
            return f"Error during explanation: {str(e)}"
    
    def transform_with_validation(self, tlr_text: str, instruction: str, 
                              transpose_flag: bool, rhythm_flag: bool, 
                              style_flag: bool, harmonic_flag: bool) -> Tuple[str, str]:
        """Transform music with hard validation barriers"""
        if not tlr_text.strip():
            return "", "Please upload and parse a MusicXML file first."
        
        if not instruction.strip():
            return tlr_text, "Please enter a transformation instruction."
        
        # Build transformation flags set
        allowed_flags = set()
        if transpose_flag:
            allowed_flags.add('transpose')
        if rhythm_flag:
            allowed_flags.add('rhythm_simplify')
        if style_flag:
            allowed_flags.add('style_change')
        if harmonic_flag:
            allowed_flags.add('harmonic_reharm')
        
        if not allowed_flags:
            return tlr_text, "Please select at least one transformation type."
        
        try:
            # Store original score for validation
            self.original_score = self.current_score
            
            # Build enhanced prompt with transformation constraints
            transformation_constraints = self.transformation_validator.get_transformation_prompt_additions(allowed_flags)
            enhanced_system_prompt = self.llm.system_prompt + "\n" + transformation_constraints
            
            # Transform with LLM using constrained prompt
            transformed_tlr, llm_errors = self.llm._call_ollama(enhanced_system_prompt, 
                                                                 f"{tlr_text}\n\nInstruction:\n{instruction}")
            
            if llm_errors:
                return tlr_text, f"LLM errors: {'; '.join(llm_errors)}"
            
            # Validate transformed TLR
            parsed_score, validation_errors = self.tlr_parser.parse(transformed_tlr)
            
            if validation_errors:
                error_msg = "Validation errors:\n" + "\n".join(validation_errors)
                return transformed_tlr, error_msg
            
            # Apply hard transformation validation
            if self.original_score is not None and parsed_score is not None:
                is_valid, transformation_errors = self.transformation_validator.validate_transformation(
                    self.original_score, parsed_score, allowed_flags
                )
            else:
                is_valid = True
                transformation_errors = []
            
            if not is_valid:
                error_msg = "Transformation validation failed:\n" + "\n".join(transformation_errors)
                error_msg += "\n\nThe LLM performed disallowed transformations. Please try again with clearer instructions."
                return tlr_text, error_msg
            
            # Store valid result
            self.current_score = parsed_score
            self.transformation_flags = allowed_flags
            
            # Generate diff
            current_tlr = self._get_current_notation_display()
            diff_html = self.diff_viewer.create_diff(
                self.original_tlr or "", current_tlr, "html"
            )
            
            flag_names = ", ".join(allowed_flags)
            return current_tlr, f"Successfully transformed music using: {flag_names}. Check diff view for details."
            
        except Exception as e:
            return tlr_text, f"Error during transformation: {str(e)}"
    
    def show_diff_view(self) -> str:
        """Show diff view between original and transformed TLR"""
        if not self.original_tlr or not self.current_score:
            return "No transformation to compare."
        
        current_tlr = self._get_current_notation_display()
        diff_html = self.diff_viewer.create_diff(
            self.original_tlr, current_tlr, "html"
        )
        
        return diff_html
    
    def update_transformation_flags(self, transpose: bool, rhythm: bool, style: bool, harmonic: bool) -> str:
        """Update current transformation flags"""
        flags = []
        if transpose:
            flags.append('transpose')
        if rhythm:
            flags.append('rhythm_simplify')
        if style:
            flags.append('style_change')
        if harmonic:
            flags.append('harmonic_reharm')
        
        self.transformation_flags = set(flags)
        return f"Active transformation flags: {', '.join(flags)}"
    
    def transform_music(self, tlr_text: str, instruction: str) -> Tuple[str, str]:
        """Transform music using LLM"""
        if not tlr_text.strip():
            return "", "Please upload and parse a MusicXML file first."
        
        if not instruction.strip():
            return tlr_text, "Please enter a transformation instruction."
        
        try:
            # Transform with LLM
            transformed_tlr, llm_errors = self.llm.transform_music(tlr_text, instruction)
            
            if llm_errors:
                return tlr_text, f"LLM errors: {'; '.join(llm_errors)}"
            
            # Validate transformed TLR
            parsed_score, validation_errors = self.tlr_parser.parse(transformed_tlr)
            
            if validation_errors:
                error_msg = "Validation errors:\n" + "\n".join(validation_errors)
                return transformed_tlr, error_msg
            
            # Store valid result
            self.current_score = parsed_score
            
            # Return display in current notation
            display_tlr = self._get_current_notation_display()
            
            return display_tlr, "Successfully transformed and validated music."
            
        except Exception as e:
            return tlr_text, f"Error during transformation: {str(e)}"
    
    def export_musicxml(self, tlr_text: str) -> Optional[str]:
        """Export TLR to MusicXML for download"""
        if not tlr_text.strip() or self.current_score is None:
            return None
        
        try:
            # Create temporary file for export
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".musicxml")
            temp_file.close()
            
            # Export to MusicXML
            success = self.exporter.export(self.current_score, temp_file.name)
            
            if success:
                self.output_file = temp_file.name
                return temp_file.name
            else:
                os.unlink(temp_file.name)
                return None
                
        except Exception as e:
            return None
    
    def create_interface(self):
        """Create Gradio interface"""
        with gr.Blocks(title="Choral LLM Workbench") as interface:
            gr.Markdown("# Choral LLM Workbench")
            gr.Markdown("Transform and analyze choral music using LLM - MusicXML → TLR → LLM → MusicXML")
            
            # Mode selection section
            with gr.Row():
                mode_choice = gr.Radio(
                    choices=[("Transformation Mode", "transform"), 
                             ("Explanation Mode", "explain")],
                    value="transform",
                    label="Working Mode",
                    info="Transform music or analyze transformations"
                )
            
            # File upload section
            with gr.Row():
                file_upload = gr.File(
                    label="Upload MusicXML",
                    file_types=[".xml", ".musicxml"]
                )
                upload_status = gr.Textbox(
                    label="Status",
                    interactive=False,
                    placeholder="Upload a MusicXML file to begin"
                )
            
            # Ollama configuration section
            with gr.Accordion("🤖 LLM Configuration", open=False):
                with gr.Row():
                    model_dropdown = gr.Dropdown(
                        choices=[],
                        value="llama3:latest",
                        label="Select Ollama Model",
                        info="Choose which LLM model to use for transformations"
                    )
                    refresh_btn = gr.Button("🔄 Refresh Models", size="sm")
                    
                ollama_status = gr.Textbox(
                    label="Ollama Status",
                    value="Checking connection...",
                    interactive=False
                )
            
            # Notation selection section
            with gr.Row():
                notation_choice = gr.Radio(
                    choices=[("Scientific Pitch Notation (SPN)", "spn"), 
                             ("Helmholtz Notation", "helmholtz")],
                    value="spn",
                    label="Notation Display",
                    info="Choose how to display pitch notation"
                )
            
            # Content display section
            with gr.Row():
                with gr.Column(scale=2):
                    tlr_display = gr.Textbox(
                        label="TLR (Textual LLM Representation)",
                        lines=12,
                        interactive=True,
                        placeholder="MusicXML will be converted to TLR format here..."
                    )
                
                with gr.Column(scale=1):
                    event_summary = gr.Textbox(
                        label="Event Summary (Explanation Mode)",
                        lines=12,
                        interactive=False,
                        placeholder="Event IDs and locations will appear here in explanation mode...",
                        visible=False
                    )
            
            # Control sections (conditional based on mode)
            with gr.Group():
                # Transformation section
                with gr.Row(visible=True) as transform_section:
                    with gr.Column(scale=1):
                        # Transformation flags
                        gr.Markdown("**Allowed Transformation Types:**")
                        transpose_flag = gr.Checkbox(
                            label="Transpose",
                            info="Change pitch by semitones (maintain intervals)",
                            value=True
                        )
                        rhythm_flag = gr.Checkbox(
                            label="Rhythm Simplify",
                            info="Simplify rhythmic patterns",
                            value=False
                        )
                        style_flag = gr.Checkbox(
                            label="Style Change",
                            info="Change musical style while preserving structure",
                            value=False
                        )
                        harmonic_flag = gr.Checkbox(
                            label="Harmonic Reharm",
                            info="Reharmonize while preserving melody",
                            value=False
                        )
                        
                        flag_status = gr.Textbox(
                            label="Active Flags",
                            interactive=False,
                            placeholder="Active transformation flags will appear here..."
                        )
                    
                    with gr.Column(scale=2):
                        instruction_input = gr.Textbox(
                            label="Transformation Instruction",
                            placeholder="e.g., Transpose everything up a minor third",
                            lines=3
                        )
                        
                        transform_status = gr.Textbox(
                            label="Status",
                            interactive=False,
                            placeholder="Select flags and enter instruction, then click Transform"
                        )
                        transform_btn = gr.Button("Transform Music", variant="primary")
                
                # Explanation section
                with gr.Row(visible=False) as explain_section:
                    with gr.Column(scale=2):
                        question_input = gr.Textbox(
                            label="Question about the Music",
                            placeholder="e.g., Why was the F# in Alto measure 12 lowered?",
                            lines=2
                        )
                    
                    with gr.Column(scale=1):
                        explanation_status = gr.Textbox(
                            label="Status",
                            interactive=False,
                            placeholder="Ask a question and click Explain"
                        )
                        explain_btn = gr.Button("Explain Music", variant="secondary")
            
            # Diff view section
            with gr.Row(visible=True) as diff_section:
                with gr.Column():
                    diff_html = gr.HTML(
                        label="Diff View",
                        value="<p>No transformation to compare. Upload and transform music to see diff.</p>",
                        interactive=False
                    )
                    show_diff_btn = gr.Button("Refresh Diff View", variant="secondary", size="sm")
            
            # Common buttons
            with gr.Row():
                export_btn = gr.Button("Export MusicXML", variant="primary")
            
            # Download section
            with gr.Row():
                download_file = gr.File(
                    label="Download MusicXML",
                    visible=False
                )
            
            # Example section
            gr.Markdown("## Examples")
            
            with gr.Tabs():
                with gr.TabItem("Transformation Examples"):
                    gr.Examples(
                        examples=[
                            ["Transpose everything up a minor third"],
                            ["Simplify the rhythm to straight quarter notes"],
                            ["Add simple passing tones between large intervals"],
                            ["Convert to homophonic texture"],
                            ["Reharmonize using secondary dominants"]
                        ],
                        inputs=[instruction_input]
                    )
                
                with gr.TabItem("Explanation Questions"):
                    gr.Examples(
                        examples=[
                            ["Why was the F# in Alto voice measure 12 lowered?"],
                            ["What harmonic progression occurs in measures 8-12?"],
                            ["Explain the voice leading in the soprano part"],
                            ["Why was the rhythm simplified in measure 4?"],
                            ["What key changes occur throughout the piece?"]
                        ],
                        inputs=[question_input]
                    )
                
                with gr.TabItem("Transformation Combinations"):
                    gr.Markdown("""
                    ### Common Flag Combinations:
                    
                    **Transpose + Rhythm Simplify**: 
                    ```
                    Flags: [✓] Transpose, [✓] Rhythm Simplify
                    Instruction: "Transpose up a major third and simplify to quarter notes"
                    ```
                    
                    **Style Change + Harmonic Reharm**:
                    ```
                    Flags: [✓] Style Change, [✓] Harmonic Reharm
                    Instruction: "Convert to baroque style and reharmonize with figured bass"
                    ```
                    
                    **All Four Flags**:
                    ```
                    Flags: [✓] Transpose, [✓] Rhythm Simplify, [✓] Style Change, [✓] Harmonic Reharm
                    Instruction: "Transpose down a fifth, simplify rhythm, convert to classical style, and reharmonize"
                    ```
                    """)
            
            # Event handlers
            file_upload.upload(
                fn=self.upload_and_parse,
                inputs=[file_upload],
                outputs=[tlr_display, upload_status]
            )
            
            mode_choice.change(
                fn=self.switch_mode,
                inputs=[mode_choice],
                outputs=[tlr_display, upload_status, event_summary]
            ).then(
                lambda mode: (gr.update(visible=(mode == "transform")), 
                            gr.update(visible=(mode == "explain")),
                            gr.update(visible=True)),
                inputs=[mode_choice],
                outputs=[transform_section, explain_section, diff_section]
            )
            
            notation_choice.change(
                fn=self.switch_notation,
                inputs=[notation_choice],
                outputs=[tlr_display]
            )
            
            # Ollama event handlers
            def refresh_models():
                if self.llm.check_connection():
                    try:
                        models = self.llm.get_available_models()
                        if models:
                            model_names = [model.get('name', model) for model in models if isinstance(model, dict)]
                            return gr.update(choices=model_names, value=self.llm.model_name), "✅ Connected - Found " + str(len(model_names)) + " models"
                        else:
                            return gr.update(), "⚠️ Connected but no models found"
                    except Exception as e:
                        return gr.update(), f"❌ Error: {str(e)}"
                else:
                    return gr.update(), "❌ Cannot connect to Ollama (localhost:11434)"
            
            def update_model(model_name):
                self.llm.set_model(model_name)
                return f"✅ Model changed to {model_name}"
            
            # Initialize on load
            interface.load(
                fn=refresh_models,
                outputs=[model_dropdown, ollama_status]
            )
            
            refresh_btn.click(
                fn=refresh_models,
                outputs=[model_dropdown, ollama_status]
            )
            
            model_dropdown.change(
                fn=update_model,
                inputs=[model_dropdown],
                outputs=[ollama_status]
            )
            
            # Update flag status when flags change
            transpose_flag.change(
                fn=self.update_transformation_flags,
                inputs=[transpose_flag, rhythm_flag, style_flag, harmonic_flag],
                outputs=[flag_status]
            )
            rhythm_flag.change(
                fn=self.update_transformation_flags,
                inputs=[transpose_flag, rhythm_flag, style_flag, harmonic_flag],
                outputs=[flag_status]
            )
            style_flag.change(
                fn=self.update_transformation_flags,
                inputs=[transpose_flag, rhythm_flag, style_flag, harmonic_flag],
                outputs=[flag_status]
            )
            harmonic_flag.change(
                fn=self.update_transformation_flags,
                inputs=[transpose_flag, rhythm_flag, style_flag, harmonic_flag],
                outputs=[flag_status]
            )
            
            transform_btn.click(
                fn=self.transform_with_validation,
                inputs=[tlr_display, instruction_input, transpose_flag, rhythm_flag, style_flag, harmonic_flag],
                outputs=[tlr_display, transform_status]
            ).then(
                fn=self.show_diff_view,
                outputs=[diff_html]
            )
            
            show_diff_btn.click(
                fn=self.show_diff_view,
                outputs=[diff_html]
            )
            
            explain_btn.click(
                fn=self.explain_music,
                inputs=[question_input],
                outputs=[explanation_status]
)
            
            export_btn.click(
                fn=lambda tlr_text: gr.File(value=self.export_musicxml(tlr_text), visible=True) if self.export_musicxml(tlr_text) else gr.File(visible=False),
                inputs=[tlr_display],
                outputs=[download_file]
            )
        
        return interface
    
    def launch(self, **kwargs):
        """Launch Gradio interface"""
        interface = self.create_interface()
        interface.launch(**kwargs)


def main():
    """Main entry point"""
    app = ChoralWorkbench()
    
    # Check Ollama connection
    if not app.llm.check_connection():
        print("Warning: Could not connect to Ollama. Make sure Ollama is running on localhost:11434")
    
    # Launch interface
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False
    )


if __name__ == "__main__":
    main()