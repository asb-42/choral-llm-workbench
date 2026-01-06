"""
Input validation utilities for the Choral LLM Workbench.

This module provides validation functions for various types of input
to ensure data integrity and security throughout the application.
"""

import os
import re
from pathlib import Path
from typing import Union, List, Optional, Any, Dict
from music21 import stream

from core.constants import ValidationLimits, FileExtensions, VoiceInfo
from core.exceptions import (
    ValidationError, InvalidFileTypeError, FileSizeError,
    InvalidTuningError, InvalidScoreError, VoiceDetectionError
)


def validate_musicxml_path(file_path: Union[str, Path]) -> Path:
    """Validate MusicXML file path and existence.
    
    Args:
        file_path: Path to the MusicXML file
        
    Returns:
        Validated Path object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        InvalidFileTypeError: If file has wrong extension
        FileSizeError: If file is too large
    """
    path_obj = Path(file_path)
    
    # Check if file exists
    if not path_obj.exists():
        raise FileNotFoundError(str(path_obj))
    
    # Check file extension
    valid_extensions = [FileExtensions.MUSICXML, FileExtensions.MUSICXML_COMPRESSED]
    if path_obj.suffix.lower() not in valid_extensions:
        raise InvalidFileTypeError(
            str(path_obj), 
            valid_extensions, 
            path_obj.suffix.lower()
        )
    
    # Check file size
    file_size = path_obj.stat().st_size
    max_size = 50 * 1024 * 1024  # 50 MB
    if file_size > max_size:
        raise FileSizeError(str(path_obj), file_size, max_size)
    
    return path_obj


def validate_base_tuning(tuning: float) -> float:
    """Validate base tuning frequency.
    
    Args:
        tuning: Base tuning frequency in Hz
        
    Returns:
        Validated tuning frequency
        
    Raises:
        InvalidTuningError: If tuning is out of valid range
    """
    if not isinstance(tuning, (int, float)):
        raise InvalidTuningError(
            float(tuning) if hasattr(tuning, '__float__') else 0.0,
            ValidationLimits.MIN_TUNING,
            ValidationLimits.MAX_TUNING
        )
    
    if not ValidationLimits.MIN_TUNING <= tuning <= ValidationLimits.MAX_TUNING:
        raise InvalidTuningError(
            tuning,
            ValidationLimits.MIN_TUNING,
            ValidationLimits.MAX_TUNING
        )
    
    return float(tuning)


def validate_tempo(tempo: Union[int, float]) -> float:
    """Validate tempo value.
    
    Args:
        tempo: Tempo in BPM
        
    Returns:
        Validated tempo
        
    Raises:
        ValidationError: If tempo is out of valid range
    """
    if not isinstance(tempo, (int, float)):
        raise ValidationError(
            f"Invalid tempo type: {type(tempo)}",
            field="tempo",
            value=tempo
        )
    
    if not ValidationLimits.MIN_TEMPO <= tempo <= ValidationLimits.MAX_TEMPO:
        raise ValidationError(
            f"Tempo {tempo} BPM is out of range ({ValidationLimits.MIN_TEMPO}-{ValidationLimits.MAX_TEMPO} BPM)",
            field="tempo",
            value=tempo
        )
    
    return float(tempo)


def validate_voice_name(voice: str) -> str:
    """Validate voice name.
    
    Args:
        voice: Voice name (e.g., "soprano", "alto", "tenor", "bass")
        
    Returns:
        Validated voice name
        
    Raises:
        ValidationError: If voice name is invalid
    """
    if not isinstance(voice, str):
        raise ValidationError(
            f"Voice name must be a string, got {type(voice)}",
            field="voice",
            value=voice
        )
    
    normalized_voice = voice.lower().strip()
    if normalized_voice not in VoiceInfo.SATB_VOICES:
        raise ValidationError(
            f"Invalid voice: {voice}. Must be one of: {', '.join(VoiceInfo.SATB_VOICES)}",
            field="voice",
            value=voice
        )
    
    return normalized_voice


def validate_llm_prompt(prompt: str, max_length: int = 1000) -> str:
    """Validate LLM prompt.
    
    Args:
        prompt: LLM prompt string
        max_length: Maximum allowed prompt length
        
    Returns:
        Validated prompt
        
    Raises:
        ValidationError: If prompt is invalid
    """
    if not isinstance(prompt, str):
        raise ValidationError(
            f"Prompt must be a string, got {type(prompt)}",
            field="prompt",
            value=prompt
        )
    
    # Remove leading/trailing whitespace
    cleaned_prompt = prompt.strip()
    
    # Check minimum length
    if len(cleaned_prompt) < 3:
        raise ValidationError(
            "Prompt must be at least 3 characters long",
            field="prompt",
            value=cleaned_prompt
        )
    
    # Check maximum length
    if len(cleaned_prompt) > max_length:
        raise ValidationError(
            f"Prompt too long: {len(cleaned_prompt)} characters (max: {max_length})",
            field="prompt",
            value=cleaned_prompt
        )
    
    # Check for potentially malicious content
    dangerous_patterns = [
        r'<script.*?>.*?</script>',  # Script tags
        r'javascript:',              # JavaScript protocol
        r'data:',                    # Data protocol
        r'vbscript:',                # VBScript protocol
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, cleaned_prompt, re.IGNORECASE):
            raise ValidationError(
                "Prompt contains potentially dangerous content",
                field="prompt",
                value=cleaned_prompt
            )
    
    return cleaned_prompt


def validate_score_structure(score: stream.Score) -> stream.Score:
    """Validate music21 score structure.
    
    Args:
        score: Music21 Score object
        
    Returns:
        Validated score
        
    Raises:
        InvalidScoreError: If score has invalid structure
        VoiceDetectionError: If no valid voices are detected
    """
    if not isinstance(score, stream.Score):
        raise InvalidScoreError(
            f"Expected Score object, got {type(score)}",
            issue="Invalid object type"
        )
    
    # Check if score has parts
    if len(score.parts) == 0:
        raise InvalidScoreError(
            "Score has no parts",
            issue="No parts found"
        )
    
    # Check if score has measures
    has_measures = False
    for part in score.parts:
        if len(part.getElementsByClass('Measure')) > 0:
            has_measures = True
            break
    
    if not has_measures:
        raise InvalidScoreError(
            "Score has no measures",
            issue="No measures found"
        )
    
    # Validate voice detection
    detected_voices = []
    for part in score.parts:
        # Simple voice detection based on part name or instrument
        part_name = getattr(part, 'partName', '').lower()
        instrument_name = ''
        if hasattr(part, 'getInstrument'):
            instrument = part.getInstrument()
            if instrument:
                instrument_name = getattr(instrument, 'instrumentName', '').lower()
        
        # Check for voice indicators
        voice_indicators = VoiceInfo.SATB_VOICES + ['s', 'a', 't', 'b']
        for indicator in voice_indicators:
            if indicator in part_name or indicator in instrument_name:
                if indicator in VoiceInfo.SATB_VOICES:
                    detected_voices.append(indicator)
                elif indicator in ['s', 'a', 't', 'b']:
                    voice_map = {'s': 'soprano', 'a': 'alto', 't': 'tenor', 'b': 'bass'}
                    detected_voices.append(voice_map[indicator])
                break
    
    if not detected_voices:
        raise VoiceDetectionError(
            "No SATB voices detected in score",
            detected_voices=[]
        )
    
    return score


def validate_session_id(session_id: str) -> str:
    """Validate session ID format.
    
    Args:
        session_id: Session ID string
        
    Returns:
        Validated session ID
        
    Raises:
        ValidationError: If session ID is invalid
    """
    if not isinstance(session_id, str):
        raise ValidationError(
            f"Session ID must be a string, got {type(session_id)}",
            field="session_id",
            value=session_id
        )
    
    # Check length
    if len(session_id) < 8 or len(session_id) > 64:
        raise ValidationError(
            f"Session ID length must be between 8 and 64 characters",
            field="session_id",
            value=session_id
        )
    
    # Check format (alphanumeric with some special characters)
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        raise ValidationError(
            "Session ID can only contain letters, numbers, underscores, and hyphens",
            field="session_id",
            value=session_id
        )
    
    return session_id


def validate_file_upload(file_obj: Any, max_size_mb: int = 50) -> Dict[str, Any]:
    """Validate uploaded file object.
    
    Args:
        file_obj: Uploaded file object (from Gradio or similar)
        max_size_mb: Maximum file size in MB
        
    Returns:
        Dictionary with file information
        
    Raises:
        ValidationError: If file is invalid
        FileSizeError: If file is too large
    """
    if not file_obj:
        raise ValidationError(
            "No file provided",
            field="file"
        )
    
    # Get file information
    if hasattr(file_obj, 'name'):
        file_name = file_obj.name
    elif isinstance(file_obj, str):
        file_name = file_obj
    else:
        raise ValidationError(
            f"Invalid file object type: {type(file_obj)}",
            field="file"
        )
    
    # Check file extension
    file_path = Path(file_name)
    valid_extensions = [FileExtensions.MUSICXML, FileExtensions.MUSICXML_COMPRESSED]
    if file_path.suffix.lower() not in valid_extensions:
        raise InvalidFileTypeError(
            file_name,
            valid_extensions,
            file_path.suffix.lower()
        )
    
    # Check file size if available
    file_size = 0
    if hasattr(file_obj, 'size'):
        file_size = file_obj.size
    elif hasattr(file_obj, 'seek') and hasattr(file_obj, 'tell'):
        # Try to get size by seeking to end
        current_pos = file_obj.tell()
        file_obj.seek(0, 2)  # Seek to end
        file_size = file_obj.tell()
        file_obj.seek(current_pos)  # Restore position
    
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise FileSizeError(file_name, file_size, max_size_bytes)
    
    return {
        'name': file_name,
        'size': file_size,
        'extension': file_path.suffix.lower(),
        'valid': True
    }


def validate_measure_range(start_measure: int, end_measure: int, 
                          total_measures: int) -> tuple[int, int]:
    """Validate measure range.
    
    Args:
        start_measure: Starting measure number
        end_measure: Ending measure number
        total_measures: Total number of measures in score
        
    Returns:
        Tuple of validated (start_measure, end_measure)
        
    Raises:
        ValidationError: If measure range is invalid
    """
    # Validate types
    if not isinstance(start_measure, int) or not isinstance(end_measure, int):
        raise ValidationError(
            "Measure numbers must be integers",
            field="measures"
        )
    
    # Validate ranges
    if start_measure < 1:
        raise ValidationError(
            f"Start measure must be >= 1, got {start_measure}",
            field="start_measure",
            value=start_measure
        )
    
    if end_measure > total_measures:
        raise ValidationError(
            f"End measure cannot exceed total measures ({total_measures}), got {end_measure}",
            field="end_measure",
            value=end_measure
        )
    
    if start_measure > end_measure:
        raise ValidationError(
            f"Start measure ({start_measure}) cannot be greater than end measure ({end_measure})",
            field="measures"
        )
    
    return start_measure, end_measure


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path separators
    sanitized = filename.replace('/', '_').replace('\\', '_')
    
    # Remove dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f]', '', sanitized)
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = "unnamed_file"
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext
    
    return sanitized


def validate_json_data(data: Dict[str, Any], required_keys: List[str]) -> Dict[str, Any]:
    """Validate JSON data structure.
    
    Args:
        data: Dictionary to validate
        required_keys: List of required keys
        
    Returns:
        Validated data
        
    Raises:
        ValidationError: If data structure is invalid
    """
    if not isinstance(data, dict):
        raise ValidationError(
            f"Expected dictionary, got {type(data)}",
            field="data"
        )
    
    # Check required keys
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        raise ValidationError(
            f"Missing required keys: {', '.join(missing_keys)}",
            field="data"
        )
    
    return data


def validate_audio_format(format_type: str) -> str:
    """Validate audio format type.
    
    Args:
        format_type: Audio format (e.g., "wav", "mp3", "midi")
        
    Returns:
        Validated format type
        
    Raises:
        ValidationError: If format is invalid
    """
    valid_formats = ["wav", "mp3", "midi", "mid"]
    normalized_format = format_type.lower().strip()
    
    if normalized_format not in valid_formats:
        raise ValidationError(
            f"Invalid audio format: {format_type}. Valid formats: {', '.join(valid_formats)}",
            field="format",
            value=format_type
        )
    
    return normalized_format