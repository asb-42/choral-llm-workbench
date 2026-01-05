import yaml
from pathlib import Path

class Config:
    """
    Globale Konfigurationsklasse für die Choral-LLM-Workbench.
    Lädt Einstellungen aus config.yaml.
    """

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"
        self.config_path = Path(config_path)
        self._data = self._load_config()

        # Audio-Grundeinstellungen
        self.audio_tuning_default = self._data.get("audio_tuning_default", 432.0)
        self.audio_tuning_options = self._data.get("audio_tuning_options", [432.0, 440.0, 443.0])

    def _load_config(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def get(self, key, default=None):
        return self._data.get(key, default)
