# File: core/config.py

import yaml
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.yaml")

class Config:
    """
    Global configuration for the application.
    Reads settings from config.yaml.
    Provides access to base_tuning and other options.
    """

    def __init__(self, config_file=CONFIG_FILE):
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                self.settings = yaml.safe_load(f)
        else:
            self.settings = {}

    @property
    def base_tuning(self):
        """
        Return the base tuning frequency (Hz) from config.
        Default: 432 Hz.
        """
        return self.settings.get("base_tuning", 432)

# Global singleton
config = Config()
