"""
Custom exceptions for the Choral LLM Workbench.

This module defines all custom exception classes to provide
consistent error handling and meaningful error messages.
"""

from typing import Optional, Any, Dict
from core.i18n import _


class ChoralWorkbenchError(Exception):
    """Base exception for all Choral Workbench errors."""
    
    def __init__(self, message: str, key: Optional[str] = None, **kwargs):
        """Initialize the base exception.
        
        Args:
            message: Error message
            key: Translation key for i18n
            **kwargs: Additional context for formatting
        """
        super().__init__(message)
        self.message = message
        self.translation_key = key or "error.general"
        self.context = kwargs
    
    def get_localized_message(self) -> str:
        """Get localized error message.
        
        Returns:
            Localized error message
        """
        return _(self.translation_key, error=self.message, **self.context)


class ValidationError(ChoralWorkbenchError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 value: Optional[Any] = None, **kwargs):
        """Initialize validation error.
        
        Args:
            message: Error message
            field: Name of the field that failed validation
            value: The invalid value
            **kwargs: Additional context
        """
        super().__init__(message, "error.validation", 
                        field=field, value=value, **kwargs)
        self.field = field
        self.value = value


class FileError(ChoralWorkbenchError):
    """Base class for file-related errors."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 **kwargs):
        """Initialize file error.
        
        Args:
            message: Error message
            file_path: Path to the problematic file
            **kwargs: Additional context
        """
        super().__init__(message, **kwargs)
        self.file_path = file_path


class FileNotFoundError(FileError):
    """Raised when a required file is not found."""
    
    def __init__(self, file_path: str, **kwargs):
        """Initialize file not found error.
        
        Args:
            file_path: Path to the missing file
            **kwargs: Additional context
        """
        message = f"File not found: {file_path}"
        super().__init__(message, file_path, "error.file_not_found", 
                        path=file_path, **kwargs)


class InvalidFileTypeError(FileError):
    """Raised when a file has an invalid type."""
    
    def __init__(self, file_path: str, expected_types: list[str], 
                 actual_type: Optional[str] = None, **kwargs):
        """Initialize invalid file type error.
        
        Args:
            file_path: Path to the invalid file
            expected_types: List of expected file types
            actual_type: The actual file type detected
            **kwargs: Additional context
        """
        self.expected_types = expected_types
        self.actual_type = actual_type
        
        message = f"Invalid file type: {actual_type or 'unknown'}. Expected: {', '.join(expected_types)}"
        super().__init__(message, file_path, "file.invalid_type",
                        file_type=actual_type, expected_types=', '.join(expected_types), 
                        **kwargs)


class FileSizeError(FileError):
    """Raised when a file is too large."""
    
    def __init__(self, file_path: str, file_size: int, max_size: int, **kwargs):
        """Initialize file size error.
        
        Args:
            file_path: Path to the oversized file
            file_size: Actual file size in bytes
            max_size: Maximum allowed file size in bytes
            **kwargs: Additional context
        """
        self.file_size = file_size
        self.max_size = max_size
        
        message = f"File too large: {file_size} bytes (max: {max_size} bytes)"
        super().__init__(message, file_path, "file.too_large",
                        max_size=max_size / (1024*1024), **kwargs)


class ScoreError(ChoralWorkbenchError):
    """Base class for score-related errors."""
    
    def __init__(self, message: str, score_info: Optional[Dict[str, Any]] = None, 
                 **kwargs):
        """Initialize score error.
        
        Args:
            message: Error message
            score_info: Additional score information
            **kwargs: Additional context
        """
        super().__init__(message, **kwargs)
        self.score_info = score_info or {}


class ScoreParsingError(ScoreError):
    """Raised when MusicXML score parsing fails."""
    
    def __init__(self, file_path: str, parse_error: Optional[Exception] = None, 
                 **kwargs):
        """Initialize score parsing error.
        
        Args:
            file_path: Path to the problematic score file
            parse_error: The original parsing exception
            **kwargs: Additional context
        """
        self.parse_error = parse_error
        
        message = f"Failed to parse MusicXML score: {file_path}"
        if parse_error:
            message += f" - {str(parse_error)}"
        
        super().__init__(message, {"file_path": file_path}, 
                        "score.parse_failed", error=str(parse_error) if parse_error else "", 
                        **kwargs)


class InvalidScoreError(ScoreError):
    """Raised when a score has invalid structure or content."""
    
    def __init__(self, message: str, issue: Optional[str] = None, **kwargs):
        """Initialize invalid score error.
        
        Args:
            message: Error message
            issue: Specific issue description
            **kwargs: Additional context
        """
        self.issue = issue
        super().__init__(message, {"issue": issue}, **kwargs)


class VoiceDetectionError(ScoreError):
    """Raised when voice detection fails."""
    
    def __init__(self, message: str, detected_voices: Optional[list[str]] = None, 
                 **kwargs):
        """Initialize voice detection error.
        
        Args:
            message: Error message
            detected_voices: List of voices that were detected
            **kwargs: Additional context
        """
        self.detected_voices = detected_voices or []
        super().__init__(message, {"detected_voices": detected_voices}, 
                        **kwargs)


class AudioError(ChoralWorkbenchError):
    """Base class for audio-related errors."""
    
    def __init__(self, message: str, audio_info: Optional[Dict[str, Any]] = None, 
                 **kwargs):
        """Initialize audio error.
        
        Args:
            message: Error message
            audio_info: Additional audio information
            **kwargs: Additional context
        """
        super().__init__(message, **kwargs)
        self.audio_info = audio_info or {}


class AudioRenderingError(AudioError):
    """Raised when audio rendering fails."""
    
    def __init__(self, message: str, render_step: Optional[str] = None, 
                 **kwargs):
        """Initialize audio rendering error.
        
        Args:
            message: Error message
            render_step: The step where rendering failed
            **kwargs: Additional context
        """
        self.render_step = render_step
        super().__init__(message, {"render_step": render_step}, 
                        "audio.render_failed", error=message, **kwargs)


class SoundFontNotFoundError(AudioError):
    """Raised when SoundFont file is not found."""
    
    def __init__(self, soundfont_path: str, **kwargs):
        """Initialize SoundFont not found error.
        
        Args:
            soundfont_path: Path to the missing SoundFont
            **kwargs: Additional context
        """
        self.soundfont_path = soundfont_path
        
        message = f"SoundFont not found: {soundfont_path}"
        super().__init__(message, {"soundfont_path": soundfont_path}, 
                        "audio.no_soundfont", **kwargs)


class InvalidTuningError(ValidationError):
    """Raised when tuning frequency is invalid."""
    
    def __init__(self, tuning: float, min_tuning: float, max_tuning: float, 
                 **kwargs):
        """Initialize invalid tuning error.
        
        Args:
            tuning: The invalid tuning frequency
            min_tuning: Minimum allowed tuning
            max_tuning: Maximum allowed tuning
            **kwargs: Additional context
        """
        self.tuning = tuning
        self.min_tuning = min_tuning
        self.max_tuning = max_tuning
        
        message = f"Invalid tuning frequency: {tuning} Hz. Must be between {min_tuning} and {max_tuning} Hz"
        super().__init__(message, "tuning", tuning, 
                        "error.invalid_tuning", tuning=tuning, min=min_tuning, 
                        max=max_tuning, **kwargs)


class LLMError(ChoralWorkbenchError):
    """Base class for LLM-related errors."""
    
    def __init__(self, message: str, llm_info: Optional[Dict[str, Any]] = None, 
                 **kwargs):
        """Initialize LLM error.
        
        Args:
            message: Error message
            llm_info: Additional LLM information
            **kwargs: Additional context
        """
        super().__init__(message, **kwargs)
        self.llm_info = llm_info or {}


class LLMConnectionError(LLMError):
    """Raised when connection to LLM service fails."""
    
    def __init__(self, service_url: str, connection_error: Optional[Exception] = None, 
                 **kwargs):
        """Initialize LLM connection error.
        
        Args:
            service_url: URL of the LLM service
            connection_error: The original connection exception
            **kwargs: Additional context
        """
        self.service_url = service_url
        self.connection_error = connection_error
        
        message = f"Failed to connect to LLM service: {service_url}"
        if connection_error:
            message += f" - {str(connection_error)}"
        
        super().__init__(message, {"service_url": service_url}, 
                        "llm.no_connection", **kwargs)


class LLMTimeoutError(LLMError):
    """Raised when LLM request times out."""
    
    def __init__(self, timeout_seconds: int, **kwargs):
        """Initialize LLM timeout error.
        
        Args:
            timeout_seconds: Timeout duration in seconds
            **kwargs: Additional context
        """
        self.timeout_seconds = timeout_seconds
        
        message = f"LLM request timed out after {timeout_seconds} seconds"
        super().__init__(message, {"timeout": timeout_seconds}, 
                        "llm.timeout", **kwargs)


class LLMGenerationError(LLMError):
    """Raised when LLM text generation fails."""
    
    def __init__(self, prompt: str, generation_error: Optional[Exception] = None, 
                 **kwargs):
        """Initialize LLM generation error.
        
        Args:
            prompt: The prompt that failed
            generation_error: The original generation exception
            **kwargs: Additional context
        """
        self.prompt = prompt
        self.generation_error = generation_error
        
        message = "LLM text generation failed"
        if generation_error:
            message += f": {str(generation_error)}"
        
        super().__init__(message, {"prompt": prompt}, 
                        "llm.generation_failed", error=str(generation_error) if generation_error else "", 
                        **kwargs)


class SessionError(ChoralWorkbenchError):
    """Base class for session-related errors."""
    
    def __init__(self, message: str, session_id: Optional[str] = None, 
                 **kwargs):
        """Initialize session error.
        
        Args:
            message: Error message
            session_id: ID of the problematic session
            **kwargs: Additional context
        """
        super().__init__(message, **kwargs)
        self.session_id = session_id


class SessionNotFoundError(SessionError):
    """Raised when a session is not found."""
    
    def __init__(self, session_id: str, **kwargs):
        """Initialize session not found error.
        
        Args:
            session_id: ID of the missing session
            **kwargs: Additional context
        """
        message = f"Session not found: {session_id}"
        super().__init__(message, session_id, "session.not_found", 
                        session_id=session_id, **kwargs)


class SessionCorruptedError(SessionError):
    """Raised when a session file is corrupted."""
    
    def __init__(self, session_id: str, corruption_details: Optional[str] = None, 
                 **kwargs):
        """Initialize session corrupted error.
        
        Args:
            session_id: ID of the corrupted session
            corruption_details: Details about the corruption
            **kwargs: Additional context
        """
        self.corruption_details = corruption_details
        
        message = f"Session corrupted: {session_id}"
        if corruption_details:
            message += f" - {corruption_details}"
        
        super().__init__(message, session_id, "session.corrupted", **kwargs)


class ConfigurationError(ChoralWorkbenchError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, 
                 config_value: Optional[Any] = None, **kwargs):
        """Initialize configuration error.
        
        Args:
            message: Error message
            config_key: The problematic configuration key
            config_value: The invalid configuration value
            **kwargs: Additional context
        """
        self.config_key = config_key
        self.config_value = config_value
        super().__init__(message, **kwargs)


class NetworkError(ChoralWorkbenchError):
    """Base class for network-related errors."""
    
    def __init__(self, message: str, url: Optional[str] = None, 
                 status_code: Optional[int] = None, **kwargs):
        """Initialize network error.
        
        Args:
            message: Error message
            url: URL that was being accessed
            status_code: HTTP status code
            **kwargs: Additional context
        """
        super().__init__(message, "error.network", url=url, 
                        status_code=status_code, **kwargs)
        self.url = url
        self.status_code = status_code


class PermissionError(ChoralWorkbenchError):
    """Raised when permission is denied for an operation."""
    
    def __init__(self, operation: str, resource: Optional[str] = None, **kwargs):
        """Initialize permission error.
        
        Args:
            operation: The operation that was denied
            resource: The resource being accessed
            **kwargs: Additional context
        """
        self.operation = operation
        self.resource = resource
        
        message = f"Permission denied: {operation}"
        if resource:
            message += f" on {resource}"
        
        super().__init__(message, "error.permission", error=message, **kwargs)