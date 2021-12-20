from pathlib import Path
import logging
from typing import Optional, Set

from .osbook_utils import read_osbooks, write_osbooks
from .models import OSBook
from .utils import read_yml
from .models import Args


def extract_resources(osbooks: Set[OSBook], pipeline: dict):
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


def extract_and_save(
    clean: bool,
    input_file: Optional[Path] = None,
    output_file: Optional[Path] = None,
):
    if not clean:
        osbooks = read_osbooks(output_file)
    else:
        osbooks: Set[OSBook] = set()
    if input_file is None:
        from .models.concourse_handler import ConcourseHandler
        handler = ConcourseHandler.get()
        pipeline = handler.get_pipeline("sync-osbooks")
    else:
        pipeline = read_yml(input_file)
    extract_resources(osbooks, pipeline)
    write_osbooks(osbooks, output_file)


def main(args: Args):
    extract_and_save(args.clean, args.file, args.outfile)
