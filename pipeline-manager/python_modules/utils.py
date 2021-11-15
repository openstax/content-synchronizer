from pathlib import Path
from typing import Any

import yaml

def read_yml(file_path: Path):
    with open(file_path, "r") as yaml_in:
        return yaml.load(yaml_in, Loader=yaml.SafeLoader)

def write_yml(to_dump: Any, file_path: Path):
    with open(file_path, "w") as yaml_out:
        yaml.dump(to_dump, yaml_out)