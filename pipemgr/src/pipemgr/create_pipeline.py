import re
from pathlib import Path

from . import TEMPLATE_ROOT
from .utils import ask_confirm, read_yml, write_yml, load_yaml
from .osbook_utils import OSBOOKS_FILE
from .manage_books import print_diff, get_books_diff
from .models import Args, ConcourseHandler

PIPELINE_FILE = Path(".").resolve()/"sync-osbooks.yml"


class OSBooksError(Exception):
    def __init__(self):
        self.message = "Cannot create pipeline without books"

    def __str__(self) -> str:
        return self.message


def read_template(temp_path: str) -> str:
    return (TEMPLATE_ROOT/temp_path).read_text()


def prepare_template(template: str, args: dict) -> str:
    # Use what is inside {{}} as keys to the args dict
    return re.sub(
        "({{)(.+?)(}})", lambda match: args[match.group(2)], template)


def create_pipeline(osbooks_path: Path):
    if not osbooks_path.exists():
        raise OSBooksError
    # NOTE: read_yml instead of read_osbooks because we want a list of dicts here
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


def upload_changes(pipeline: dict, yes: bool):
    concourse = ConcourseHandler.get()
    diff = get_books_diff(pipeline)

    if diff.empty:
        print("No changes to upload.")
        return

    print_diff(diff)

    prompt = "Update the sync-osbooks pipeline on concourse with the above changes?"
    if yes or ask_confirm(prompt):
        concourse.set_pipeline("sync-osbooks", pipeline)


def main(args: Args):
    outfile = args.outfile
    pipeline = create_pipeline(
        args.file or OSBOOKS_FILE,
    )
    if outfile is not None:
        write_yml(pipeline, outfile)
    else:
        upload_changes(pipeline, args.yes)
