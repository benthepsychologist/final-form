import os
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class FinalFormGlobalConfig:
    """Global configuration for Final Form."""
    default_measure_registry_path: str | None = None
    default_form_binding_registry_path: str | None = None

def get_final_form_home() -> Path:
    """Get the finalform home directory.

    Default: ~/.config/finalform
    Override with FINAL_FORM_HOME environment variable.
    """
    home = os.environ.get("FINAL_FORM_HOME", "~/.config/finalform")
    return Path(home).expanduser()

def get_registry_root() -> Path:
    """Get the registry root directory.

    Returns: ~/.config/finalform/registry
    """
    return get_final_form_home() / "registry"

def get_measure_registry_path() -> Path:
    """Get the measure registry path."""
    return get_registry_root() / "measure-registry"

def get_binding_registry_path() -> Path:
    """Get the form binding registry path."""
    return get_registry_root() / "form-binding-registry"

def get_global_config_path() -> Path:
    return get_final_form_home() / "config.yaml"

def load_global_config() -> FinalFormGlobalConfig:
    path = get_global_config_path()
    if not path.exists():
        return FinalFormGlobalConfig()

    try:
        data = yaml.safe_load(path.read_text()) or {}
        return FinalFormGlobalConfig(**data)
    except Exception:
        return FinalFormGlobalConfig()
