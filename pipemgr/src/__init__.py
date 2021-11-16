from pathlib import Path

import yaml

MODULE_ROOT = Path(__file__).resolve().parent
WORKING_ROOT = MODULE_ROOT.parent
OUTPUT_ROOT = WORKING_ROOT/"out"
TEMPLATE_ROOT = MODULE_ROOT/"templates"


def load_yaml(yaml_str: str):
    return yaml.load(yaml_str, Loader=yaml.SafeLoader)


if not OUTPUT_ROOT.exists():
    OUTPUT_ROOT.mkdir()
