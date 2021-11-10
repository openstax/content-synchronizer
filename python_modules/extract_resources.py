import sys
import logging

import yaml
from .osbook_utils import read_osbooks, write_osbooks, OSBook
from .utils import read_yml
from .models import Args

def _load_stdin_yml():
    return yaml.load(sys.stdin, Loader=yaml.SafeLoader)

def main(args: Args):
    if not args.clean:
        osbooks = read_osbooks()
    else:
        osbooks = set()
    if args.file is None:
        pipeline = _load_stdin_yml()
    else:
        from pathlib import Path
        pipeline = read_yml(Path(args.file).resolve())
    if "resources" not in pipeline:
        logging.warn("No resources found")
        return
    resources = pipeline["resources"]
    for resource in resources:
        resource_type = resource["type"]
        if resource_type not in ("version-checker", "archive-api"):
            continue
        osbooks.add(OSBook.from_pipeline_resource(resource))
    if len(osbooks) == 0:
        logging.warn("No books found")
        return
    write_osbooks(osbooks)