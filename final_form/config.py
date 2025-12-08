import os
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class FinalFormGlobalConfig:
    """Global configuration for Final Form."""
    default_measure_registry_path: Optional[str] = None
    default_form_binding_registry_path: Optional[str] = None

def get_final_form_home() -> Path:
    """Get the final-form home directory.

    Default: ~/.config/final-form
    Override with FINAL_FORM_HOME environment variable.
    """
    home = os.environ.get("FINAL_FORM_HOME", "~/.config/final-form")
    return Path(home).expanduser()

def get_registry_root() -> Path:
    """Get the registry root directory.

    Returns: ~/.config/final-form/registry
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
