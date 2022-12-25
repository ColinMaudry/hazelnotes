import toml
from pathlib import Path

conf = toml.load('config.toml')
conf["data_directory"] = Path(conf["data_directory"])
conf["md_directory"] = conf["data_directory"] / "notes"


