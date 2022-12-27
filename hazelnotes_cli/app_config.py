import toml
from pathlib import Path
import os

try:
    conf = toml.load('config.toml')[os.environ.get('HAZELNOTE_TEST_PROFILE')]
except KeyError:
    conf = toml.load('config.toml')['default']

conf["data_directory"] = Path(conf["data_directory"])
conf["md_directory"] = conf["data_directory"] / "notes"



