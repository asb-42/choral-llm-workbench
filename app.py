import gradio as gr
import os
import tempfile
from typing import Tuple, Optional
from musicxml_parser import MusicXMLParser
from tlr_converter import TLRConverter
from tlr_parser import TLRParser
from ollama_llm import OllamaLLM
from musicxml_exporter import MusicXMLExporter


class ChoralWorkbench:
    """Main application class for the Choral LLM Workbench"""
    
    def __init__(self):
        self.parser = MusicXMLParser()
        self.tlr_converter = TLRConverter()
        self.tlr_parser = TLRParser()
        self.llm = OllamaLLM()
        self.exporter = MusicXMLExporter()
        
        # State
        self.current_score = None
        self.current_tlr = None
        self.output_file = None
    
    def upload_and_parse(self, file_obj) -> Tuple[str, str]:
        """Upload MusicXML file and convert to TLR"""
        if file_obj is None:
            return "", "Please upload a MusicXML file."
        
        try:
            # Parse MusicXML
            self.current_score = self.parser.parse(file_obj.name)
            
            # Convert to TLR
            self.current_tlr = self.tlr_converter.ikr_to_tlr(self.current_score)
            
            return self.current_tlr, "Successfully parsed MusicXML file."
            
        except Exception as e:
            return "", f"Error parsing file: {str(e)}"
    
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
            self.current_tlr = transformed_tlr
            
            return transformed_tlr, "Successfully transformed and validated music."
            
        except Exception as e:
            return tlr_text, f"Error during transformation: {str(e)}"
    
    def export_musicxml(self, tlr_text: str) -> Optional[str]:
        """Export TLR to MusicXML for download"""
        if not tlr_text.strip():
            return None
        
        try:
            # Parse current TLR to get score
            parsed_score, validation_errors = self.tlr_parser.parse(tlr_text)
            
            if validation_errors:
                return None
            
            # Create temporary file for export
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".musicxml")
            temp_file.close()
            
            # Export to MusicXML
            success = self.exporter.export(parsed_score, temp_file.name)
            
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
            gr.Markdown("Transform choral music using LLM - MusicXML → TLR → LLM → MusicXML")
            
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
            
            # TLR display section
            with gr.Row():
                tlr_display = gr.Textbox(
                    label="TLR (Textual LLM Representation)",
                    lines=20,
                    interactive=True,
                    placeholder="MusicXML will be converted to TLR format here..."
                )
            
            # Transformation section
            with gr.Row():
                instruction_input = gr.Textbox(
                    label="Transformation Instruction",
                    placeholder="e.g., Transpose everything up a minor third and simplify rhythm",
                    lines=2
                )
                transform_status = gr.Textbox(
                    label="Transformation Status",
                    interactive=False,
                    placeholder="Enter instruction and click Transform"
                )
            
            # Buttons
            with gr.Row():
                transform_btn = gr.Button("Transform Music", variant="primary")
                export_btn = gr.Button("Export MusicXML", variant="secondary")
            
            # Download section
            with gr.Row():
                download_file = gr.File(
                    label="Download MusicXML",
                    visible=False
                )
            
            # Event handlers
            file_upload.upload(
                fn=self.upload_and_parse,
                inputs=[file_upload],
                outputs=[tlr_display, upload_status]
            )
            
            transform_btn.click(
                fn=self.transform_music,
                inputs=[tlr_display, instruction_input],
                outputs=[tlr_display, transform_status]
            )
            
            def export_and_show_download(tlr_text):
                output_path = self.export_musicxml(tlr_text)
                if output_path:
                    return gr.File(value=output_path, visible=True)
                else:
                    return gr.File(visible=False)
            
            export_btn.click(
                fn=export_and_show_download,
                inputs=[tlr_display],
                outputs=[download_file]
            )
            
            # Example instructions
            gr.Markdown("## Example Instructions")
            gr.Examples(
                examples=[
                    ["Transpose everything up a minor third and simplify rhythm"],
                    ["Make all note durations twice as long while preserving the musical structure"],
                    ["Add passing notes between leaps of a third or more"],
                    ["Convert to homophonic texture with quarter note accompaniment"],
                    ["Transpose down a perfect fifth and add simple counterpoint"]
                ],
                inputs=[instruction_input]
            )
        
        return interface
    
    def launch(self, **kwargs):
        """Launch the Gradio interface"""
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
        server_port=7860,
        share=False
    )


if __name__ == "__main__":
    main()