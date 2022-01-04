import logging
from pathlib import Path
from typing import Optional, Set

from . import concourse_session_factory
from .models import Args, OSBook
from .osbook_utils import read_osbooks, write_osbooks
from .utils import read_yml


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
        with concourse_session_factory() as session:
            pipeline, _ = session.get_pipeline("CE", "sync-osbooks")
    else:
        pipeline = read_yml(input_file)
    extract_resources(osbooks, pipeline)
    write_osbooks(osbooks, output_file)


def main(args: Args):
    extract_and_save(args.clean, args.file, args.outfile)
