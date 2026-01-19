"""
Status Management for Choral LLM Workbench

Provides structured status reporting and management for the UI.
"""


class StatusManager:
    """Manages application status and provides formatted status messages"""
    
    def __init__(self):
        self.current_status = "idle"
        self.status_message = "Ready"
        self.detail_message = ""
        self.current_file = None
        self.error_context = None
    
    def set_idle(self):
        """Set status to idle/ready"""
        self.current_status = "idle"
        self.status_message = "Ready"
        self.detail_message = ""
        self.current_file = None
        self.error_context = None
    
    def set_transforming(self, input_file: str):
        """Set status to transforming"""
        self.current_status = "transforming"
        self.current_file = input_file
        self.status_message = "Transforming"
        self.detail_message = f"Processing {input_file}"
    
    def set_exporting(self, output_file: str):
        """Set status to exporting"""
        self.current_status = "exporting"
        self.current_file = output_file
        self.status_message = "Exporting"
        self.detail_message = f"Generating {output_file}"
    
    def set_llm_loading(self, model_name: str, model_size: str):
        """Set status to LLM loading"""
        self.current_status = "llm_loading"
        self.status_message = "Loading LLM"
        self.detail_message = f"Loading {model_name} ({model_size})"
    
    def set_parsing_error(self, input_file: str, location: str, reason: str):
        """Set status to parsing error"""
        self.current_status = "error"
        self.status_message = "Parsing Error"
        self.current_file = input_file
        self.detail_message = f"Error in {input_file} at {location}: {reason}"
        self.error_context = {"location": location, "reason": reason}
    
    def set_llm_error(self, error_message: str):
        """Set status to LLM error"""
        self.current_status = "error"
        self.status_message = "LLM Error"
        self.detail_message = error_message
        self.error_context = {"error": error_message}
    
    def set_transformation_success(self):
        """Set status to success"""
        self.current_status = "success"
        self.status_message = "Transformation Complete"
        self.detail_message = "Music transformed successfully"
        self.error_context = None
    
    def set_validation_error(self, input_file: str, errors: list):
        """Set status to validation error"""
        self.current_status = "error"
        self.status_message = "Validation Error"
        self.current_file = input_file
        self.detail_message = f"Validation failed for {input_file}"
        self.error_context = {"errors": errors}
    
    def get_display_message(self) -> str:
        """Get formatted display message for UI"""
        if self.current_status == "idle":
            return "Ready"
        elif self.current_status == "transforming":
            return f"Transforming music file {self.current_file}"
        elif self.current_status == "exporting":
            return f"Exporting music file {self.current_file}"
        elif self.current_status == "llm_loading":
            return self.detail_message
        elif self.current_status == "error":
            return self.status_message + ": " + self.detail_message
        elif self.current_status == "success":
            return "Transformation finished successfully"
        else:
            return self.status_message
    
    def get_status_color(self) -> str:
        """Get color indicator for UI based on status"""
        if self.current_status in ["idle", "success"]:
            return "green"
        elif self.current_status in ["transforming", "exporting", "llm_loading"]:
            return "orange"
        elif self.current_status == "error":
            return "red"
        else:
            return "gray"
    
    def is_busy(self) -> bool:
        """Check if application is busy"""
        return self.current_status in ["transforming", "exporting", "llm_loading"]
