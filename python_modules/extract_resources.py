import sys
import logging

import yaml
from .osbook_utils import read_osbooks, write_osbooks, OSBook
from .utils import read_yml
from .models import Args

def main(args: Args):
    if not args.clean:
        osbooks = read_osbooks(args.outfile)
    else:
        osbooks = set()
    if args.file is None:
        pipeline = yaml.load(sys.stdin, Loader=yaml.SafeLoader)
    else:
        pipeline = read_yml(args.file)
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
    write_osbooks(osbooks, args.outfile)