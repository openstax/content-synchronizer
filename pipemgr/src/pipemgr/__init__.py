from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parent
WORKING_ROOT = Path.home()/".pipemgr"
OUTPUT_ROOT = WORKING_ROOT
TEMPLATE_ROOT = MODULE_ROOT/"templates"

if not OUTPUT_ROOT.exists():
    OUTPUT_ROOT.mkdir(parents=True)
