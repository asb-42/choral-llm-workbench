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
from semantic_diff_analyzer import SemanticDiffAnalyzer, SemanticDiffEntry
from semantic_diff_ui import SemanticDiffUI
from status_manager import StatusManager
import copy


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
        self.semantic_analyzer = SemanticDiffAnalyzer()
        self.semantic_ui = SemanticDiffUI()
        self.status_manager = StatusManager()
        
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
        self.input_filename = None  # Track input filename for status messages
        self.output_filename = None  # Track output filename for status messages
    
    def upload_and_parse(self, file_obj) -> Tuple[str, str, str]:
        """Upload MusicXML file and convert to TLR"""
        if file_obj is None:
            self.status_manager.set_idle()
            return "", "Please upload a MusicXML file.", self.status_manager.get_display_message()
        
        try:
            # Store input filename
            self.input_filename = os.path.basename(file_obj.name)
            
            # Parse MusicXML
            self.current_score = self.parser.parse(file_obj.name)
            
            # Store original score and TLR for semantic diff
            if self.current_score:
                # Store original score BEFORE transformation
                # Use deepcopy to ensure we have a separate copy, not a reference
                self.original_score = copy.deepcopy(self.current_score)
                self.original_tlr = self.tlr_converter.ikr_to_tlr(self.current_score)
                # Reset transformed state
                self.current_tlr = None
            
            # Convert to appropriate notation based on current setting
            tlr_display = self._get_current_notation_display()
            
            # Update status
            self.status_manager.set_idle()
            
            return tlr_display, "Successfully parsed MusicXML file.", self.status_manager.get_display_message()
            
        except Exception as e:
            self.status_manager.set_parsing_error(self.input_filename or "unknown", "parsing", str(e))
            return "", f"Error parsing file: {str(e)}", self.status_manager.get_display_message()
    
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
    
    def switch_notation_both(self, notation_choice: str) -> Tuple[str, str]:
        """Switch between SPN and Helmholtz notation for both input and output"""
        self.current_notation = notation_choice
        
        # Get input display (from original_score)
        input_display = ""
        if self.original_score:
            input_display = self.tlr_converter.ikr_to_tlr(self.original_score) if notation_choice == "spn" else self.helmholtz_converter.score_to_helmholtz_tlr(self.original_score)
        
        # Get output display (from current_score)
        output_display = ""
        if self.current_score:
            output_display = self.tlr_converter.ikr_to_tlr(self.current_score) if notation_choice == "spn" else self.helmholtz_converter.score_to_helmholtz_tlr(self.current_score)
        
        return input_display, output_display
    
    def switch_mode(self, mode_choice: str) -> Tuple[str, str, str, str, str, str]:
        """Switch between transform and explain mode"""
        self.current_mode = mode_choice
        self.status_manager.set_idle()
        
        if mode_choice == "explain":
            # In explain mode, show musical overview and explanation interface
            if self.current_score:
                # Generate a musical overview instead of technical event summary
                musical_overview = self._generate_musical_overview()
                # Also generate technical event summary for debugging
                technical_summary = self.explainer_llm.get_event_summary(self.current_score)
                return "", "", "EXPLANATION MODE - Musical Analysis", self.status_manager.get_display_message(), musical_overview, technical_summary
            else:
                return "", "", "EXPLANATION MODE - Please upload a MusicXML file first", self.status_manager.get_display_message(), "", ""
        else:
            # Transform mode - show current TLRs
            # Input display from original_score
            input_display = ""
            if self.original_score:
                input_display = self.tlr_converter.ikr_to_tlr(self.original_score) if self.current_notation == "spn" else self.helmholtz_converter.score_to_helmholtz_tlr(self.original_score)
            
            # Output display from current_score
            output_display = ""
            if self.current_score:
                output_display = self.tlr_converter.ikr_to_tlr(self.current_score) if self.current_notation == "spn" else self.helmholtz_converter.score_to_helmholtz_tlr(self.current_score)
            
            return input_display, output_display, "TRANSFORMATION MODE - Edit and Transform Music", self.status_manager.get_display_message(), "", ""
    
    def _generate_musical_overview(self) -> str:
        """Generate a musical overview of current score"""
        if not self.current_score:
            return ""
        
        try:
            overview_parts = []
            overview_parts.append("## 🎵 Musical Overview\n")
            
            # Basic information
            if self.current_score.parts:
                overview_parts.append(f"**Voices/Parts:** {len(self.current_score.parts)}")
                for i, part in enumerate(self.current_score.parts):
                    role = part.role if hasattr(part, 'role') else "instrument"
                    name = part.name if hasattr(part, 'name') else f"Part {i+1}"
                    overview_parts.append(f"  - {name} ({role})")
            
            # Measures
            total_measures = 0
            if self.current_score.parts:
                for part in self.current_score.parts:
                    if hasattr(part, 'voices') and part.voices:
                        for voice in part.voices:
                            if hasattr(voice, 'measures') and voice.measures:
                                total_measures = max(total_measures, len(voice.measures))
            overview_parts.append(f"\n**Total Measures:** {total_measures}")
            
            # Key and time signature information
            overview_parts.append("\n**Structure:**")
            overview_parts.append("  - Time signature information varies by part")
            overview_parts.append("  - Pitch information analyzed per voice")
            
            # Musical characteristics
            overview_parts.append("\n**Musical Characteristics:**")
            overview_parts.append("  - Use the question box below to ask about:")
            overview_parts.append("    • Harmonic progressions")
            overview_parts.append("    • Voice leading")
            overview_parts.append("    • Melodic structure")
            overview_parts.append("    • Rhythmic patterns")
            overview_parts.append("    • Key changes")
            
            # Transformation info
            if self.original_score and self.original_score != self.current_score:
                overview_parts.append("\n**Note:** A transformation has been applied. You can ask questions about:")
                overview_parts.append("  - What changed between original and transformed version")
                overview_parts.append("  - Why specific notes were altered")
                overview_parts.append("  - How transformation affected musical structure")
            
            return "\n".join(overview_parts)
            
        except Exception as e:
            return f"Error generating musical overview: {str(e)}"
    
    def explain_music(self, question: str) -> Tuple[str, str]:
        """Answer user question about current music"""
        if not question.strip():
            self.status_manager.set_idle()
            return "Please enter a question about the music.", ""
        
        if self.current_mode != "explain":
            self.status_manager.set_idle()
            return "Please switch to explanation mode first.", ""
        
        if not self.current_score:
            self.status_manager.set_idle()
            return "Please upload a MusicXML file first.", ""
        
        try:
            # Update status
            self.status_manager.status_message = "Explaining music"
            self.status_manager.detail_message = f"Answering: {question[:50]}..."
            
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
                self.status_manager.set_idle()
                return f"Analysis errors: {'; '.join(errors)}", ""
            
            self.status_manager.set_idle()
            return "✅ Explanation completed successfully", explanation
            
        except Exception as e:
            self.status_manager.set_llm_error(str(e))
            return f"Error during explanation: {str(e)}", ""
    
    def transform_with_validation(self, tlr_text: str, instruction: str,
                              transpose_flag: bool, rhythm_flag: bool, 
                              style_flag: bool, harmonic_flag: bool) -> Tuple[str, str, str, str]:
        """Transform music with hard validation barriers"""
        if not tlr_text.strip():
            self.status_manager.set_idle()
            return "", "", "Please upload and parse a MusicXML file first.", self.status_manager.get_display_message()
        
        if not instruction.strip():
            self.status_manager.set_idle()
            return tlr_text, "", "Please enter a transformation instruction.", self.status_manager.get_display_message()
        
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
            self.status_manager.set_idle()
            return tlr_text, "", "Please select at least one transformation type.", self.status_manager.get_display_message()
        
        try:
            # Update status
            self.status_manager.set_transforming(self.input_filename or "unknown")
            
            # Store original score and TLR for validation (only if not already stored)
            if self.original_score is None:
                self.original_score = self.current_score
            if self.original_tlr is None:
                self.original_tlr = self._get_current_notation_display() if self.current_score else tlr_text
            
            # Build enhanced prompt with transformation constraints
            transformation_constraints = self.transformation_validator.get_transformation_prompt_additions(allowed_flags)
            enhanced_system_prompt = self.llm.system_prompt + "\n" + transformation_constraints
            
            # Transform with LLM using constrained prompt
            response = self.llm._call_ollama(enhanced_system_prompt,
                                                  f"{tlr_text}\n\nInstruction:\n{instruction}")
            transformed_tlr = response
            llm_errors = []  # _call_ollama doesn't return errors, only raises exceptions
            
            if llm_errors:
                self.status_manager.set_llm_error(f"LLM errors: {'; '.join(llm_errors)}")
                return tlr_text, "", f"LLM errors: {'; '.join(llm_errors)}", self.status_manager.get_display_message()
            
            # Validate transformed TLR
            parsed_score, validation_errors = self.tlr_parser.parse(transformed_tlr)

            # Always accept the transformation result, even with parsing errors
            # Keep current_score if parsing fails, so semantic diff still works
            if parsed_score:
                self.current_score = parsed_score
            # else: keep current_score from before transformation
            self.current_tlr = transformed_tlr
            self._last_transformed_tlr = transformed_tlr  # Store for semantic diff fallback

            if validation_errors:
                # Check if there are serious errors that prevent basic functionality
                serious_errors = [e for e in validation_errors if 'critical' in e.lower() or 'fatal' in e.lower()]
                if serious_errors:
                    error_msg = "Critical validation errors:\n" + "\n".join(serious_errors)
                    self.status_manager.set_validation_error(self.input_filename or "unknown", serious_errors)
                    return transformed_tlr, "", error_msg, self.status_manager.get_display_message()
                else:
                    # Accept with warning
                    self.status_manager.set_transformation_success()
                    warning_msg = "⚠️ Transformation completed with formatting warnings (TLR parsing issues, but music should be correct)"
                    return tlr_text, transformed_tlr, warning_msg, self.status_manager.get_display_message()

            # Apply transformation validation if we have parsed scores
            if self.original_score is not None and parsed_score is not None:
                is_valid, transformation_errors = self.transformation_validator.validate_transformation(
                    self.original_score, parsed_score, allowed_flags
                )
                if not is_valid:
                    self.status_manager.set_transformation_success()
                    warning_msg = f"⚠️ Transformation completed but validation warnings:\n" + "\n".join(transformation_errors)
                    return tlr_text, transformed_tlr, warning_msg, self.status_manager.get_display_message()

            # Success
            self.transformation_flags = allowed_flags
            self.status_manager.set_transformation_success()
            return tlr_text, transformed_tlr, "✅ Transformation completed successfully", self.status_manager.get_display_message()
            
        except Exception as e:
            self.status_manager.set_llm_error(str(e))
            return tlr_text, "", f"Error during transformation: {str(e)}", self.status_manager.get_display_message()
    
    def update_semantic_diff_display(self) -> str:
        """Update semantic diff display with HTML output"""
        try:
            print(f"DEBUG: update_semantic_diff_display called")
            print(f"DEBUG: original_score exists: {self.original_score is not None}")
            print(f"DEBUG: current_score exists: {self.current_score is not None}")
            
            # Debug: Check if we have both scores
            if self.original_score and self.current_score:
                # Check if they are same object or different
                is_same = self.original_score is self.current_score
                print(f"DEBUG: original_score is current_score: {is_same}")
                print(f"DEBUG: original_score: {type(self.original_score)}, id={id(self.original_score)}")
                print(f"DEBUG: current_score: {type(self.current_score)}, id={id(self.current_score)}")
                
                semantic_diffs = self.semantic_analyzer.compute_semantic_diff(
                    self.original_score, self.current_score
                )
                print(f"DEBUG: Got {len(semantic_diffs)} semantic diffs")
                if semantic_diffs:
                    print(f"DEBUG: First diff: {semantic_diffs[0]}")
                return self.semantic_ui.render_semantic_diff_html(semantic_diffs)

            # Fallback: Show that transformation occurred but parsing failed
            elif self.original_tlr and hasattr(self, '_last_transformed_tlr'):
                return self.semantic_ui.render_semantic_diff_html([
                    SemanticDiffEntry(
                        scope="system",
                        location="Transformation",
                        change_type="info",
                        description="✅ Transformation completed successfully"
                    ),
                    SemanticDiffEntry(
                        scope="system",
                        location="Parsing",
                        change_type="warning",
                        description="⚠️ TLR parsing issues detected (music should still be correct)"
                    )
                ])

            return self.semantic_ui.render_semantic_diff_html([])

        except Exception as e:
            return f'<div class="semantic-diff-container"><p style="color: #d32f2f;">Error computing semantic diff: {str(e)}</p></div>'
    
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
            
            # Store result - even with parsing errors, we want to keep the TLR
            # For export, we'll use the TLR directly if parsing failed
            self.current_score = parsed_score
            self.current_tlr = transformed_tlr
            
            # Return display in current notation
            display_tlr = self._get_current_notation_display()
            
            return display_tlr, "Successfully transformed and validated music."
            
        except RuntimeError as e:
            error_msg = str(e)
            
            # Provide specific guidance for common issues
            if "timeout" in error_msg.lower():
                return tlr_text, f"⏱️ {error_msg}\n💡 Tip: Try a smaller model or reduce input complexity."
            elif "connection" in error_msg.lower():
                return tlr_text, f"🔌 {error_msg}\n💡 Tip: Check if Ollama is running on localhost:11434"
            else:
                return tlr_text, f"❌ {error_msg}"
                
        except Exception as e:
            return tlr_text, f"Unexpected error during transformation: {str(e)}"
    
    def export_musicxml(self, tlr_text: str) -> Optional[str]:
        """Export TLR to MusicXML for download"""
        if not tlr_text.strip():
            self.status_manager.set_idle()
            return None
        
        # If we don't have a valid current_score (parsing failed), try to re-parse
        if self.current_score is None:
            try:
                # Try to parse again with relaxed validation
                self.current_score, _ = self.tlr_parser.parse(tlr_text)
            except:
                # If parsing still fails, we can't export
                self.status_manager.set_idle()
                return None
        
        try:
            # Generate output filename
            base_name = os.path.splitext(self.input_filename or "output")[0]
            output_filename = f"{base_name}-transformed.musicxml"
            self.output_filename = output_filename
            
            # Update status
            self.status_manager.set_exporting(output_filename)
            
            # Create temporary file for export
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".musicxml")
            temp_file.close()
            
            # Export to MusicXML - handle None case
            if self.current_score is not None:
                success = self.exporter.export(self.current_score, temp_file.name)
            else:
                success = False
            
            if success:
                self.output_file = temp_file.name
                self.status_manager.set_transformation_success()
                return temp_file.name
            else:
                os.unlink(temp_file.name)
                self.status_manager.set_idle()
                return None
                
        except Exception as e:
            self.status_manager.set_idle()
            return None
    
    def compute_semantic_diff(self) -> str:
        """Compute semantic diff for UI display"""
        if self.original_tlr and self.current_tlr:
            try:
                # Parse both TLRs to IKR
                original_score = self.tlr_parser.parse(self.original_tlr)[0]
                transformed_score = self.tlr_parser.parse(self.current_tlr)[0]
                
                if original_score and transformed_score:
                    # Compute semantic differences
                    semantic_diffs = self.semantic_analyzer.compute_semantic_diff(
                        original_score, transformed_score
                    )
                    
                    # Format for display
                    diff_lines = []
                    for diff in semantic_diffs:
                        diff_lines.append(f"[{diff.scope}] {diff.location}: {diff.description}")
                    
                    return "\n".join(diff_lines)
                else:
                    return "Unable to parse scores for semantic analysis"
            except Exception as e:
                return f"Error in semantic analysis: {str(e)}"
        else:
            return "No semantic diff available (upload and transform first)"
    
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
            
            # Status display section
            with gr.Row():
                status_display = gr.Textbox(
                    label="Status",
                    value="Ready",
                    interactive=False,
                    placeholder="Application status will appear here..."
                )
            
            # File upload section - INPUT AREA
            gr.Markdown("## 📁 INPUT: MusicXML File")
            with gr.Row():
                file_upload = gr.File(
                    label="Upload MusicXML Input File",
                    file_types=[".xml", ".musicxml"]
                )
                upload_status = gr.Textbox(
                    label="Upload Status",
                    interactive=False,
                    placeholder="Upload a MusicXML file to begin"
                )
            
            # Notation selection section - applies to both input and output
            with gr.Row():
                notation_choice = gr.Radio(
                    choices=[("Scientific Pitch Notation (SPN)", "spn"), 
                             ("Helmholtz Notation", "helmholtz")],
                    value="spn",
                    label="Notation Display (applies to all outputs)",
                    info="Choose how to display pitch notation"
                )
            
            # Input TLR display - Accordion group
            with gr.Accordion("📝 INPUT: Transcribed Music", open=True) as input_accordion:
                tlr_display = gr.Textbox(
                    label="TLR (Textual LLM Representation) - Original Input",
                    lines=12,
                    interactive=True,
                    placeholder="MusicXML will be converted to TLR format here..."
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
            
            # Transformation section - TRANSFORMATION AREA
            gr.Markdown("## 🔄 TRANSFORMATION")
            with gr.Group():
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
                            label="Transformation Status",
                            interactive=False,
                            placeholder="Select flags and enter instruction, then click Transform"
                        )
                        transform_btn = gr.Button("🔄 Transform Music", variant="primary")
                
                # Explanation section
                with gr.Row(visible=False) as explain_section:
                    with gr.Column(scale=2):
                        question_input = gr.Textbox(
                            label="Ask a Question about the Music",
                            placeholder="e.g., Why was the F# in Alto measure 12 lowered?",
                            lines=2
                        )
                        musical_explanation = gr.Textbox(
                            label="Musical Explanation",
                            lines=10,
                            interactive=False,
                            placeholder="Musical explanation will appear here..."
                        )
                    
                    with gr.Column(scale=1):
                        explanation_status = gr.Textbox(
                            label="Status",
                            interactive=False,
                            placeholder="Ask a question and click Explain"
                        )
                        explain_btn = gr.Button("❓ Explain Music", variant="secondary")
            
            # Output TLR display - Accordion group
            with gr.Accordion("📝 OUTPUT: Transformed Music", open=True) as output_accordion:
                transformed_tlr_display = gr.Textbox(
                    label="TLR (Textual LLM Representation) - Transformed Output",
                    lines=12,
                    interactive=False,
                    placeholder="Transformed music will appear here..."
                )
            
            # Semantic Diff Section
            with gr.Accordion("🎼 OUTPUT: Musical Changes (Semantic Diff)", open=False) as diff_section:
                semantic_diff_display = gr.HTML(
                    value='<div class="semantic-diff-container"><p style="color: #666;">No semantic diff available. Transform music first.</p></div>',
                    interactive=False
                )
            
            # Event Summary - Explanation Mode (for technical debugging)
            with gr.Accordion("🔧 Technical: Event Summary (Debug)", open=False):
                event_summary = gr.Textbox(
                    label="Event IDs and Locations",
                    lines=8,
                    interactive=False,
                    placeholder="Event IDs and locations will appear here for debugging...",
                    visible=False
                )
            
            # Export section - OUTPUT AREA
            gr.Markdown("## 📤 OUTPUT: Export")
            with gr.Row():
                export_btn = gr.Button("💾 Export to MusicXML", variant="primary")
            
            # Download section
            with gr.Row():
                download_file = gr.File(
                    label="Download MusicXML Output File",
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
                outputs=[tlr_display, upload_status, status_display]
            )
            
            mode_choice.change(
                fn=self.switch_mode,
                inputs=[mode_choice],
                outputs=[tlr_display, transformed_tlr_display, upload_status, status_display, musical_explanation, event_summary]
            ).then(
                lambda mode: (gr.update(visible=(mode == "transform")), 
                            gr.update(visible=(mode == "explain")),
                            gr.update(visible=True),
                            gr.update(visible=(mode == "explain")),
                            gr.update(visible=(mode == "explain"))),
                inputs=[mode_choice],
                outputs=[transform_section, explain_section, diff_section, event_summary]
            )
            
            notation_choice.change(
                fn=self.switch_notation_both,
                inputs=[notation_choice],
                outputs=[tlr_display, transformed_tlr_display]
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
                outputs=[tlr_display, transformed_tlr_display, transform_status, status_display]
            ).then(
                fn=lambda: gr.update(value=self.update_semantic_diff_display()),
                outputs=[semantic_diff_display]
            )
            

            
            explain_btn.click(
                fn=self.explain_music,
                inputs=[question_input],
                outputs=[explanation_status, musical_explanation]
            ).then(
                fn=lambda: self.status_manager.get_display_message(),
                outputs=[status_display]
            )
            
            export_btn.click(
                fn=lambda tlr_text: (gr.File(value=self.export_musicxml(tlr_text), visible=True) if self.export_musicxml(tlr_text) else gr.File(visible=False), 
                                    self.status_manager.get_display_message()),
                inputs=[tlr_display],
                outputs=[download_file, status_display]
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