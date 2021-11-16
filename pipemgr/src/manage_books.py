from .osbook_utils import OSBook, read_osbooks, write_osbooks
from .models import Args

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

def list_books(args):
    for book in read_osbooks(args.file):
        print(book)