"""
Internationalization (i18n) framework for the Choral LLM Workbench.

This module provides translation support and localization utilities
to make the application accessible in multiple languages.
"""

import gettext
import json
from pathlib import Path
from typing import Dict, Optional, Any
from core.constants import PathDefaults, APP_NAME


class I18nManager:
    """Manages internationalization and localization for the application."""
    
    def __init__(self, locale_dir: Path = PathDefaults.LOCALES_DIR, 
                 default_locale: str = "en"):
        """Initialize the i18n manager.
        
        Args:
            locale_dir: Directory containing translation files
            default_locale: Default language locale (e.g., "en", "de")
        """
        self.locale_dir = Path(locale_dir)
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.translations: Dict[str, gettext.GNUTranslations] = {}
        self.fallback_translations: Dict[str, Dict[str, str]] = {}
        
        # Load translations
        self._load_translations()
        self._load_fallback_translations()
    
    def _load_translations(self) -> None:
        """Load gettext translation files."""
        if not self.locale_dir.exists():
            return
        
        for locale_dir in self.locale_dir.iterdir():
            if locale_dir.is_dir():
                try:
                    translation = gettext.translation(
                        APP_NAME.lower().replace(" ", "_"),
                        localedir=self.locale_dir,
                        languages=[locale_dir.name]
                    )
                    self.translations[locale_dir.name] = translation
                except FileNotFoundError:
                    # No translation file found for this locale
                    continue
    
    def _load_fallback_translations(self) -> None:
        """Load JSON fallback translations for development."""
        fallback_file = self.locale_dir / "fallback_translations.json"
        if fallback_file.exists():
            try:
                with open(fallback_file, 'r', encoding='utf-8') as f:
                    self.fallback_translations = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
    
    def set_locale(self, locale: str) -> None:
        """Set the current locale.
        
        Args:
            locale: Language locale (e.g., "en", "de")
        """
        if locale in self.translations or locale in self.fallback_translations:
            self.current_locale = locale
        else:
            # Fallback to default locale
            self.current_locale = self.default_locale
    
    def get_text(self, key: str, **kwargs) -> str:
        """Get translated text for the given key.
        
        Args:
            key: Translation key (e.g., "ui.musicxml_input")
            **kwargs: Formatting parameters
            
        Returns:
            Translated text string
        """
        # Try gettext first
        if self.current_locale in self.translations:
            translation = self.translations[self.current_locale]
            translation.install()
            try:
                # Use gettext translation
                translated = translation.gettext(key)
                if translated != key:  # Translation found
                    return translated.format(**kwargs) if kwargs else translated
            except Exception:
                pass
        
        # Try fallback translations
        if self.current_locale in self.fallback_translations:
            locale_translations = self.fallback_translations[self.current_locale]
            if key in locale_translations:
                return locale_translations[key].format(**kwargs) if kwargs else locale_translations[key]
        
        # Try default locale
        if self.default_locale in self.fallback_translations:
            default_translations = self.fallback_translations[self.default_locale]
            if key in default_translations:
                return default_translations[key].format(**kwargs) if kwargs else default_translations[key]
        
        # Return key as last resort
        return key.format(**kwargs) if kwargs else key
    
    def get_available_locales(self) -> list[str]:
        """Get list of available locales.
        
        Returns:
            List of available locale codes
        """
        locales = set(self.translations.keys())
        locales.update(self.fallback_translations.keys())
        return sorted(list(locales))
    
    def format_number(self, number: float, locale: Optional[str] = None) -> str:
        """Format number according to locale conventions.
        
        Args:
            number: Number to format
            locale: Target locale (uses current if None)
            
        Returns:
            Formatted number string
        """
        target_locale = locale or self.current_locale
        
        # Simple locale-based formatting
        if target_locale == "de":
            return f"{number:.2f}".replace(".", ",")
        else:
            return f"{number:.2f}"
    
    def format_frequency(self, frequency: float, locale: Optional[str] = None) -> str:
        """Format frequency with appropriate units.
        
        Args:
            frequency: Frequency in Hz
            locale: Target locale
            
        Returns:
            Formatted frequency string
        """
        formatted = self.format_number(frequency, locale)
        return f"{formatted} Hz"
    
    def format_tempo(self, tempo: float, locale: Optional[str] = None) -> str:
        """Format tempo with appropriate units.
        
        Args:
            tempo: Tempo in BPM
            locale: Target locale
            
        Returns:
            Formatted tempo string
        """
        formatted = self.format_number(tempo, locale)
        return f"{formatted} BPM"


# Global i18n instance
_i18n_manager = I18nManager()


def get_i18n() -> I18nManager:
    """Get the global i18n manager instance.
    
    Returns:
        Global I18nManager instance
    """
    return _i18n_manager


def set_locale(locale: str) -> None:
    """Set the global locale.
    
    Args:
        locale: Language locale
    """
    _i18n_manager.set_locale(locale)


def _(key: str, **kwargs) -> str:
    """Shorthand function for getting translated text.
    
    Args:
        key: Translation key
        **kwargs: Formatting parameters
        
    Returns:
        Translated text string
    """
    return _i18n_manager.get_text(key, **kwargs)


def create_translation_template() -> Dict[str, str]:
    """Create a template with all translatable strings.
    
    Returns:
        Dictionary with translation keys and default English text
    """
    return {
        # UI Elements
        "ui.musicxml_input": "MusicXML Input",
        "ui.llm_prompt": "LLM Prompt",
        "ui.base_tuning": "Base Tuning (Hz)",
        "ui.render_audio": "Render Audio",
        "ui.download_score": "Download Score",
        "ui.soprano_prompt": "Soprano Prompt",
        "ui.alto_prompt": "Alto Prompt", 
        "ui.tenor_prompt": "Tenor Prompt",
        "ui.bass_prompt": "Bass Prompt",
        "ui.harmonize": "Harmonize",
        "ui.ghost_chords": "Ghost Chords",
        "ui.accept": "Accept",
        "ui.reject": "Reject",
        "ui.undo": "Undo",
        "ui.redo": "Redo",
        "ui.save_session": "Save Session",
        "ui.load_session": "Load Session",
        
        # File operations
        "file.upload_success": "File uploaded successfully: {filename}",
        "file.upload_failed": "Failed to upload file: {error}",
        "file.invalid_type": "Invalid file type. Please upload a MusicXML file.",
        "file.too_large": "File too large. Maximum size is {max_size} MB.",
        
        # Audio operations
        "audio.rendering": "Rendering audio...",
        "audio.render_success": "Audio rendered successfully",
        "audio.render_failed": "Failed to render audio: {error}",
        "audio.no_soundfont": "SoundFont not found. Please check audio configuration.",
        
        # LLM operations
        "llm.generating": "Generating harmonization...",
        "llm.generation_success": "Harmonization generated successfully",
        "llm.generation_failed": "Failed to generate harmonization: {error}",
        "llm.no_connection": "No connection to LLM service",
        "llm.timeout": "LLM request timed out",
        
        # Session operations
        "session.created": "Session created: {session_id}",
        "session.loaded": "Session loaded successfully",
        "session.saved": "Session saved successfully",
        "session.not_found": "Session not found: {session_id}",
        "session.corrupted": "Session file is corrupted",
        
        # Score operations
        "score.parsing": "Parsing MusicXML score...",
        "score.parsed": "Score parsed successfully",
        "score.parse_failed": "Failed to parse score: {error}",
        "score.no_voices": "No voices detected in score",
        "score.invalid_harmony": "Invalid harmony detected",
        
        # Voice information
        "voice.soprano": "Soprano",
        "voice.alto": "Alto",
        "voice.tenor": "Tenor", 
        "voice.bass": "Bass",
        "voice.unknown": "Unknown Voice",
        
        # Error messages
        "error.general": "An error occurred: {error}",
        "error.validation": "Validation error: {error}",
        "error.network": "Network error: {error}",
        "error.file_not_found": "File not found: {path}",
        "error.permission": "Permission denied: {error}",
        
        # Success messages
        "success.changes_applied": "Changes applied successfully",
        "success.file_saved": "File saved successfully: {filename}",
        "success.audio_exported": "Audio exported successfully: {filename}",
        
        # Help text
        "help.musicxml_format": "Upload a MusicXML file (.xml or .mxl) containing SATB voices",
        "help.llm_prompt": "Enter a prompt for the LLM to generate harmonization",
        "help.base_tuning": "Select the base tuning frequency for audio rendering",
        "help.voice_prompt": "Enter a specific prompt for this voice part",
    }


def save_translation_template() -> None:
    """Save the translation template to the fallback translations file."""
    template = create_translation_template()
    
    # Ensure locales directory exists
    PathDefaults.LOCALES_DIR.mkdir(exist_ok=True)
    
    # Save as fallback translations
    fallback_file = PathDefaults.LOCALES_DIR / "fallback_translations.json"
    fallback_data = {
        "en": template,
        "de": {key: value for key, value in template.items()}  # Copy English as base
    }
    
    try:
        with open(fallback_file, 'w', encoding='utf-8') as f:
            json.dump(fallback_data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Failed to save translation template: {e}")


# Auto-save translation template if it doesn't exist
if not (PathDefaults.LOCALES_DIR / "fallback_translations.json").exists():
    save_translation_template()