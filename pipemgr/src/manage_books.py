from .osbook_utils import read_osbooks, write_osbooks
from .models import Args, OSBook


def _ask_confirm(book) -> bool:
    response = input(f"Are you sure you want to delete {book}? ").lower()
    return response in ("y", "yes")


def add_book(args: Args):
    osbooks = read_osbooks(args.file)
    osbooks.add(OSBook(args.book, args.server))
    write_osbooks(osbooks, args.file)


def remove_book(args: Args):
    osbooks = read_osbooks(args.file)
    book = OSBook(args.book, args.server)
    if book not in osbooks:
        raise Exception(f"{book} was not in the osbooks collection")
    if args.yes or _ask_confirm(book):
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
