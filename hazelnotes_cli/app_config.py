import toml
from pathlib import Path
import os

def get_config(profile: str = None) -> dict:
    if not profile:
        if 'PYTEST_CURRENT_TEST' in os.environ:
            profile = "test"
        else:
            profile = "default"

    conf = toml.load('config.toml')[profile]
    conf["data_directory"] = Path(conf["data_directory"])
    conf["md_directory"] = conf["data_directory"] / "notes"
    return conf





