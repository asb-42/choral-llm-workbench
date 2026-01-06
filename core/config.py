"""
Enhanced configuration management for the Choral LLM Workbench.

This module provides a robust configuration system using dataclasses
and proper validation to ensure consistent configuration handling.
"""

import os
import yaml
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from core.constants import (
    AudioDefaults, LLMDefaults, UIDefaults, SessionDefaults,
    LoggingDefaults, PathDefaults, APIDefaults, FeatureFlags
)
from core.validation import validate_base_tuning
from core.exceptions import ConfigurationError


@dataclass
class AudioConfig:
    """Audio rendering configuration."""
    base_tuning: float = AudioDefaults.BASE_TUNING
    tuning_options: List[float] = field(default_factory=lambda: AudioDefaults.TUNING_OPTIONS.copy())
    default_soundfont: str = AudioDefaults.DEFAULT_SOUNDFONT
    sample_rate: int = AudioDefaults.SAMPLE_RATE
    bit_depth: int = AudioDefaults.BIT_DEPTH
    channels: int = AudioDefaults.CHANNELS
    voice_ranges: Dict[str, Dict[str, int]] = field(default_factory=lambda: AudioDefaults.VOICE_RANGES.copy())
    
    def __post_init__(self):
        """Validate audio configuration after initialization."""
        # Validate base tuning
        self.base_tuning = validate_base_tuning(self.base_tuning)
        
        # Validate tuning options
        validated_options = []
        for option in self.tuning_options:
            try:
                validated_options.append(validate_base_tuning(option))
            except ConfigurationError:
                # Skip invalid options
                continue
        self.tuning_options = validated_options
        
        # Ensure base_tuning is in tuning_options
        if self.base_tuning not in self.tuning_options:
            self.tuning_options.append(self.base_tuning)
            self.tuning_options.sort()


@dataclass
class LLMConfig:
    """LLM integration configuration."""
    max_tokens: int = LLMDefaults.MAX_TOKENS
    temperature: float = LLMDefaults.TEMPERATURE
    top_p: float = LLMDefaults.TOP_P
    timeout: int = LLMDefaults.TIMEOUT
    voice_prompts: Dict[str, str] = field(default_factory=lambda: LLMDefaults.VOICE_PROMPTS.copy())
    service_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: str = "default"
    
    def __post_init__(self):
        """Validate LLM configuration after initialization."""
        # Validate temperature
        if not 0.0 <= self.temperature <= 2.0:
            raise ConfigurationError(
                f"LLM temperature must be between 0.0 and 2.0, got {self.temperature}",
                config_key="llm.temperature",
                config_value=self.temperature
            )
        
        # Validate top_p
        if not 0.0 <= self.top_p <= 1.0:
            raise ConfigurationError(
                f"LLM top_p must be between 0.0 and 1.0, got {self.top_p}",
                config_key="llm.top_p",
                config_value=self.top_p
            )
        
        # Validate timeout
        if self.timeout <= 0:
            raise ConfigurationError(
                f"LLM timeout must be positive, got {self.timeout}",
                config_key="llm.timeout",
                config_value=self.timeout
            )


@dataclass
class UIConfig:
    """User interface configuration."""
    theme: str = UIDefaults.THEME
    cache_examples: bool = UIDefaults.CACHE_EXAMPLES
    analytics_enabled: bool = UIDefaults.ANALYTICS_ENABLED
    show_progress: bool = UIDefaults.SHOW_PROGRESS
    concurrency_count: int = UIDefaults.CONCURRENCY_COUNT
    max_file_size: int = UIDefaults.MAX_FILE_SIZE
    max_files: int = UIDefaults.MAX_FILES
    language: str = "en"
    
    def __post_init__(self):
        """Validate UI configuration after initialization."""
        # Validate concurrency count
        if self.concurrency_count < 1:
            self.concurrency_count = 1
        
        # Validate file size
        if self.max_file_size < 1:
            self.max_file_size = UIDefaults.MAX_FILE_SIZE


@dataclass
class SessionConfig:
    """Session management configuration."""
    max_undo_steps: int = SessionDefaults.MAX_UNDO_STEPS
    auto_save_interval: int = SessionDefaults.AUTO_SAVE_INTERVAL
    session_timeout: int = SessionDefaults.SESSION_TIMEOUT
    session_dir: Path = field(default_factory=lambda: PathDefaults.CONFIG_DIR / "sessions")
    
    def __post_init__(self):
        """Validate session configuration after initialization."""
        # Ensure session directory is a Path object
        if isinstance(self.session_dir, str):
            self.session_dir = Path(self.session_dir)
        
        # Validate values
        if self.max_undo_steps < 1:
            self.max_undo_steps = SessionDefaults.MAX_UNDO_STEPS
        
        if self.auto_save_interval < 60:
            self.auto_save_interval = SessionDefaults.AUTO_SAVE_INTERVAL
        
        if self.session_timeout < 60:
            self.session_timeout = SessionDefaults.SESSION_TIMEOUT


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = LoggingDefaults.LEVEL
    format: str = LoggingDefaults.FORMAT
    date_format: str = LoggingDefaults.DATE_FORMAT
    max_file_size: int = LoggingDefaults.MAX_FILE_SIZE
    backup_count: int = LoggingDefaults.BACKUP_COUNT
    log_file: Optional[Path] = field(default_factory=lambda: PathDefaults.LOG_DIR / "app.log")
    
    def __post_init__(self):
        """Validate logging configuration after initialization."""
        # Ensure log_file is a Path object
        if isinstance(self.log_file, str):
            self.log_file = Path(self.log_file)
        
        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            self.level = LoggingDefaults.LEVEL


@dataclass
class PathConfig:
    """Path configuration."""
    config_dir: Path = field(default_factory=lambda: PathDefaults.CONFIG_DIR)
    cache_dir: Path = field(default_factory=lambda: PathDefaults.CACHE_DIR)
    log_dir: Path = field(default_factory=lambda: PathDefaults.LOG_DIR)
    temp_dir: Path = field(default_factory=lambda: PathDefaults.TEMP_DIR)
    locales_dir: Path = field(default_factory=lambda: PathDefaults.LOCALES_DIR)
    examples_dir: Path = field(default_factory=lambda: PathDefaults.EXAMPLES_DIR)
    
    def __post_init__(self):
        """Ensure all paths are Path objects."""
        for attr_name in ['config_dir', 'cache_dir', 'log_dir', 'temp_dir', 'locales_dir', 'examples_dir']:
            attr_value = getattr(self, attr_name)
            if isinstance(attr_value, str):
                setattr(self, attr_name, Path(attr_value))


@dataclass
class APIConfig:
    """API configuration."""
    timeout: int = APIDefaults.TIMEOUT
    max_retries: int = APIDefaults.MAX_RETRIES
    retry_delay: float = APIDefaults.RETRY_DELAY
    user_agent: str = APIDefaults.USER_AGENT
    
    def __post_init__(self):
        """Validate API configuration after initialization."""
        if self.timeout <= 0:
            self.timeout = APIDefaults.TIMEOUT
        
        if self.max_retries < 0:
            self.max_retries = APIDefaults.MAX_RETRIES
        
        if self.retry_delay < 0:
            self.retry_delay = APIDefaults.RETRY_DELAY


@dataclass
class FeatureConfig:
    """Feature flag configuration."""
    enable_llm_integration: bool = FeatureFlags.ENABLE_LLM_INTEGRATION
    enable_audio_rendering: bool = FeatureFlags.ENABLE_AUDIO_RENDERING
    enable_session_management: bool = FeatureFlags.ENABLE_SESSION_MANAGEMENT
    enable_ghost_chords: bool = FeatureFlags.ENABLE_GHOST_CHORDS
    enable_collaboration: bool = FeatureFlags.ENABLE_COLLABORATION
    enable_advanced_analysis: bool = FeatureFlags.ENABLE_ADVANCED_ANALYSIS


@dataclass
class AppConfig:
    """Main application configuration."""
    audio: AudioConfig = field(default_factory=AudioConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    session: SessionConfig = field(default_factory=SessionConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    api: APIConfig = field(default_factory=APIConfig)
    features: FeatureConfig = field(default_factory=FeatureConfig)
    
    def __post_init__(self):
        """Create necessary directories after initialization."""
        # Create essential directories
        for dir_path in [
            self.paths.config_dir,
            self.paths.cache_dir,
            self.paths.log_dir,
            self.session.session_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)


class ConfigManager:
    """Manages application configuration loading and saving."""
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        if config_file is None:
            config_file = Path("config.yaml")
        
        self.config_file = Path(config_file)
        self.config: AppConfig = AppConfig()
        
        # Load configuration if file exists
        if self.config_file.exists():
            self.load_config()
    
    def load_config(self, config_file: Optional[Union[str, Path]] = None) -> AppConfig:
        """Load configuration from YAML file.
        
        Args:
            config_file: Path to configuration file (optional)
            
        Returns:
            Loaded configuration
            
        Raises:
            ConfigurationError: If configuration loading fails
        """
        if config_file:
            self.config_file = Path(config_file)
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if config_data:
                self.config = self._dict_to_config(config_data)
            
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Failed to parse YAML configuration: {e}",
                config_key="yaml_parsing"
            )
        except IOError as e:
            raise ConfigurationError(
                f"Failed to read configuration file: {e}",
                config_key="file_io"
            )
        
        return self.config
    
    def save_config(self, config_file: Optional[Union[str, Path]] = None) -> None:
        """Save configuration to YAML file.
        
        Args:
            config_file: Path to configuration file (optional)
            
        Raises:
            ConfigurationError: If configuration saving fails
        """
        if config_file:
            self.config_file = Path(config_file)
        
        try:
            # Ensure parent directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert config to dictionary and save
            config_dict = self._config_to_dict(self.config)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        
        except IOError as e:
            raise ConfigurationError(
                f"Failed to save configuration file: {e}",
                config_key="file_io"
            )
    
    def get_config(self) -> AppConfig:
        """Get current configuration.
        
        Returns:
            Current application configuration
        """
        return self.config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration with new values.
        
        Args:
            **kwargs: Configuration values to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                config_section = getattr(self.config, key)
                if isinstance(value, dict) and hasattr(config_section, '__dict__'):
                    # Update nested configuration
                    for sub_key, sub_value in value.items():
                        if hasattr(config_section, sub_key):
                            setattr(config_section, sub_key, sub_value)
                else:
                    # Set top-level configuration
                    setattr(self.config, key, value)
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> AppConfig:
        """Convert dictionary to AppConfig object.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            AppConfig object
        """
        # Extract section configurations
        audio_data = config_dict.get('audio', {})
        llm_data = config_dict.get('llm', {})
        ui_data = config_dict.get('ui', {})
        session_data = config_dict.get('session', {})
        logging_data = config_dict.get('logging', {})
        paths_data = config_dict.get('paths', {})
        api_data = config_dict.get('api', {})
        features_data = config_dict.get('features', {})
        
        # Create configuration objects
        audio_config = AudioConfig(**audio_data)
        llm_config = LLMConfig(**llm_data)
        ui_config = UIConfig(**ui_data)
        session_config = SessionConfig(**session_data)
        logging_config = LoggingConfig(**logging_data)
        paths_config = PathConfig(**paths_data)
        api_config = APIConfig(**api_data)
        features_config = FeatureConfig(**features_data)
        
        return AppConfig(
            audio=audio_config,
            llm=llm_config,
            ui=ui_config,
            session=session_config,
            logging=logging_config,
            paths=paths_config,
            api=api_config,
            features=features_config
        )
    
    def _config_to_dict(self, config: AppConfig) -> Dict[str, Any]:
        """Convert AppConfig object to dictionary.
        
        Args:
            config: AppConfig object
            
        Returns:
            Configuration dictionary
        """
        return {
            'audio': asdict(config.audio),
            'llm': asdict(config.llm),
            'ui': asdict(config.ui),
            'session': asdict(config.session),
            'logging': asdict(config.logging),
            'paths': {
                'config_dir': str(config.paths.config_dir),
                'cache_dir': str(config.paths.cache_dir),
                'log_dir': str(config.paths.log_dir),
                'temp_dir': str(config.paths.temp_dir),
                'locales_dir': str(config.paths.locales_dir),
                'examples_dir': str(config.paths.examples_dir)
            },
            'api': asdict(config.api),
            'features': asdict(config.features)
        }


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> AppConfig:
    """Get global application configuration.
    
    Returns:
        Global AppConfig instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.get_config()


def load_global_config(config_file: Optional[Union[str, Path]] = None) -> AppConfig:
    """Load global configuration from file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Loaded configuration
    """
    global _config_manager
    _config_manager = ConfigManager(config_file)
    return _config_manager.get_config()


def save_global_config(config_file: Optional[Union[str, Path]] = None) -> None:
    """Save global configuration to file.
    
    Args:
        config_file: Path to configuration file
    """
    global _config_manager
    if _config_manager is not None:
        _config_manager.save_config(config_file)


def update_global_config(**kwargs) -> None:
    """Update global configuration.
    
    Args:
        **kwargs: Configuration values to update
    """
    global _config_manager
    if _config_manager is not None:
        _config_manager.update_config(**kwargs)


# Legacy compatibility
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.yaml")

class Config:
    """
    Legacy configuration class for backward compatibility.
    Deprecated: Use ConfigManager and AppConfig instead.
    """
    
    def __init__(self, config_file=CONFIG_FILE):
        import warnings
        warnings.warn(
            "Config class is deprecated. Use ConfigManager and AppConfig instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                self.settings = yaml.safe_load(f) or {}
        else:
            self.settings = {}

    @property
    def base_tuning(self):
        """Return the base tuning frequency (Hz) from config."""
        return self.settings.get("audio_tuning_default", 432)


# Global singleton for backward compatibility
config = Config()
