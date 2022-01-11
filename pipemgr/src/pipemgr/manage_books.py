import logging
from typing import Set

from . import concourse_session_factory
from .concourse.utils import expect
from .extract_resources import extract_resources
from .models import Args, DiffResult, OSBook
from .osbook_utils import OSBOOKS_FILE, read_osbooks, write_osbooks
from .utils import ask_confirm


def add_book(args: Args):
    osbooks = read_osbooks(args.file)
    osbooks.add(
        OSBook(expect(args.book, "BUG: expected book repo"), args.server))
    write_osbooks(osbooks, args.file)


def remove_book(args: Args):
    osbooks = read_osbooks(args.file)
    book = OSBook(expect(args.book, "BUG: expected book repo"), args.server)
    if book not in osbooks:
        logging.warning(f"{book} was not in the osbooks collection")
        return
    if args.yes or ask_confirm(f"Are you sure you want to delete '{book}'?"):
        osbooks.remove(book)
        write_osbooks(osbooks, args.file)


def list_books(args: Args):
    books = sorted(read_osbooks(args.file), key=lambda book: book.book_repo)
    to_print = map(
        (
            (lambda b: b.book_repo)
            if args.repo_only else
            str
        ),
        books
    )
    for book in to_print:
        print(book)


def get_books_diff(pipeline_a: dict, pipeline_b: dict) -> DiffResult[OSBook]:
    osbooks_current: Set[OSBook] = set()
    extract_resources(osbooks_current, pipeline_b)

    osbooks_new: Set[OSBook] = set()
    extract_resources(osbooks_new, pipeline_a)

    return DiffResult(osbooks_current, osbooks_new)


def diff_books(args: Args):
    from .create_pipeline import create_pipeline_from_file

    pipeline_a = create_pipeline_from_file(
        args.file or OSBOOKS_FILE,
    )

    with concourse_session_factory() as session:
        pipeline_b, _ = session.get_pipeline("CE", "sync-osbooks")

    diff = get_books_diff(pipeline_a, pipeline_b)
    if diff.empty:
        print("No changes.")
    else:
        diff.display_unified()
