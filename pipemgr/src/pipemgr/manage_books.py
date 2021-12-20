import logging
from typing import Optional, Set

from .osbook_utils import read_osbooks, write_osbooks, OSBOOKS_FILE
from .models import Args, OSBook
from .utils import ask_confirm
from .concourse.utils import expect
from .models import ConcourseHandler, DiffResult
from .extract_resources import extract_resources


def add_book(args: Args):
    osbooks = read_osbooks(args.file)
    osbooks.add(OSBook(expect(args.book, "BUG: expected book repo"), args.server))
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


def get_books_diff(
    pipeline_a: dict,
    pipeline_b: Optional[dict] = None
) -> DiffResult:
    diff_result = DiffResult([], [])

    if pipeline_b is None:
        concourse = ConcourseHandler.get()
        pipeline_b = concourse.get_pipeline("sync-osbooks")

    osbooks_current: Set[OSBook] = set()
    extract_resources(osbooks_current, pipeline_b)

    osbooks_new: Set[OSBook] = set()
    extract_resources(osbooks_new, pipeline_a)

    osbooks_xor = osbooks_current ^ osbooks_new

    for book in osbooks_xor:
        if book in osbooks_new:
            diff_result.added.append(book)
        else:
            diff_result.removed.append(book)

    return diff_result


def print_diff(diff: DiffResult):
    from itertools import chain

    unified = chain(
        map(lambda b: f"+ {b}", diff.added),
        map(lambda b: f"- {b}", diff.removed)
    )

    for output in sorted(unified):
        print(output)


def diff_books(args: Args):
    from .create_pipeline import create_pipeline

    pipeline = create_pipeline(
        args.file or OSBOOKS_FILE,
    )
    diff = get_books_diff(pipeline)
    if diff.empty:
        print("No changes.")
    else:
        print_diff(diff)
