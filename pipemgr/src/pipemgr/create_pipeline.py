from pathlib import Path
from typing import List

from . import TEMPLATE_ROOT, concourse_session_factory
from .manage_books import get_books_diff
from .models import Args
from .osbook_utils import OSBOOKS_FILE
from .utils import (ask_confirm, load_yaml, prepare_template, read_yml,
                    write_yml)

PIPELINE_FILE = Path(".").resolve()/"sync-osbooks.yml"


class OSBooksError(Exception):
    def __init__(self):
        self.message = "Cannot create pipeline without books"

    def __str__(self) -> str:
        return self.message


def read_template(temp_path: str) -> str:
    return (TEMPLATE_ROOT/temp_path).read_text()


def create_pipeline(osbooks: List[dict]) -> dict:
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


def create_pipeline_from_file(osbooks_path: Path):
    if not osbooks_path.exists():
        raise OSBooksError
    # NOTE: read_yml instead of read_osbooks because we want a list of dicts here
    osbooks = read_yml(osbooks_path)
    return create_pipeline(osbooks)


def upload_changes(pipeline_a: dict, yes: bool):
    with concourse_session_factory() as session:
        pipeline_b, pipeline_verison = session.get_pipeline(
            "CE", "sync-osbooks")

        diff = get_books_diff(pipeline_a, pipeline_b)

        if diff.empty:
            print("No changes to upload.")
            return

        diff.display_unified()

        prompt = "Update the sync-osbooks pipeline on concourse with the above changes?"
        if yes or ask_confirm(prompt):
            session.set_pipeline("CE", "sync-osbooks",
                                 pipeline_a, pipeline_verison)


def main(args: Args):
    outfile = args.outfile
    pipeline = create_pipeline_from_file(
        args.file or OSBOOKS_FILE
    )
    if outfile is not None:
        write_yml(pipeline, outfile)
    else:
        upload_changes(pipeline, args.yes)
