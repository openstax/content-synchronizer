from pathlib import Path
import re

import yaml
from . import TEMPLATE_ROOT
from .utils import read_yml, write_yml
from .osbook_utils import OSBOOKS_FILE
from .models import Args

PIPELINE_FILE = Path(".").resolve()/"sync-osbooks.yml"


class OSBooksError(Exception):
    def __init__(self):
        self.message = "Cannot create pipeline without books"

    def __str__(self) -> str:
        return self.message


def load_yaml(yaml_str: str):
    return yaml.load(yaml_str, Loader=yaml.SafeLoader)


def read_template(temp_path: str) -> str:
    return (TEMPLATE_ROOT/temp_path).read_text()


def prepare_template(template: str, args: dict) -> str:
    # Use what is inside {{}} as keys to the args dict
    return re.sub(
        "({{)(.+?)(}})", lambda match: args[match.group(2)], template)


def create_pipeline(osbooks_path: Path):
    if not osbooks_path.exists():
        raise OSBooksError
    osbooks = read_yml(osbooks_path)
    if len(osbooks) == 0:
        raise OSBooksError
    pipeline_temp = read_yml(TEMPLATE_ROOT/"pipeline.yml")
    job_temp = read_template("job.yml")
    arch_book_temp = read_template("archive-book.yml")
    book_repo_temp = read_template("book-repo.yml")
    jobs = pipeline_temp["jobs"]
    resources = pipeline_temp["resources"]
    for book in osbooks:
        job = prepare_template(job_temp, book)
        arch_book = prepare_template(arch_book_temp, book)
        book_repo = prepare_template(book_repo_temp, book)
        jobs.append(load_yaml(job))
        resources.append(load_yaml(arch_book))
        resources.append(load_yaml(book_repo))
    return pipeline_temp


def main(args: Args):
    outfile = args.outfile
    pipeline = create_pipeline(
        args.file or OSBOOKS_FILE,
    )
    if outfile is not None:
        write_yml(pipeline, outfile)
    else:
        from .remote import set_pipeline
        set_pipeline("sync-osbooks", pipeline)
