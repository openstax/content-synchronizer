import logging

from src.osbook_utils import read_osbooks, write_osbooks
from src.models import Args, OSBook
from src.utils import ask_confirm
from src.concourse.utils import expect


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
