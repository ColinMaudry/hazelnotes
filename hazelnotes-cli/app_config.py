import toml
from pathlib import Path

config = toml.load('../config.toml')
config["data_directory"] = Path(config["data_directory"])
config["md_directory"] = config["data_directory"] / "notes"


