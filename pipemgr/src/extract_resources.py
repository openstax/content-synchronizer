from pathlib import Path
import sys
import logging
from typing import Optional

import yaml
from .osbook_utils import read_osbooks, write_osbooks
from .models import OSBook
from .utils import read_yml
from .models import Args


def extract(
    clean: bool,
    input_file: Optional[Path] = None,
    output_file: Optional[Path] = None,
):
    if not clean:
        osbooks = read_osbooks(output_file)
    else:
        osbooks = set()
    if input_file is None:
        pipeline = yaml.load(sys.stdin, Loader=yaml.SafeLoader)
    else:
        pipeline = read_yml(input_file)
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
    write_osbooks(osbooks, output_file)


def main(args: Args):
    extract(args.clean, args.file, args.outfile)
