"""Pipe Manager

Usage:
    pipemgr create [-f FILE | --file=FILE] [-o OUTFILE | --output=OUTFILE]
    pipemgr extract [-f FILE | --file=FILE] [-o OUTFILE | --output=OUTFILE] [-c | --clean]
    pipemgr add-book BOOK [-f FILE | --file=FILE] [--server=SERVER] [-u | --update]
    pipemgr remove-book BOOK [-f FILE | --file=FILE] [--server=SERVER] [-u | --update] [-y | --yes]
    pipemgr list-books [-f FILE | --file=FILE] [-r | --repo-only]
    pipemgr (-h | --help)

Options:
    -h  --help
        Show help

    -c  --clean
        Delete stored osbooks before extracting resources from the pipeline

    -u  --update
        Update the osbooks.yml file after adding/removing booka

    -y  --yes
        Do not prompt before completing the action

    -f FILE  --file=FILE
        Use FILE as input for the operation

    -o OUTFILE  --output=OUTFILE
        Output results to OUTFILE

    -r  --repo-only
        When listing books, only list the repository name

    --server=SERVER
        The archive server for the book  [default: cnx.org]

"""

from docopt import docopt

from src import create_pipeline, extract_resources, manage_books
from src.models import Args


def cli():
    docopts = docopt(__doc__)
    args = Args.from_docopts(docopts)

    if docopts["create"]:
        create_pipeline.main(args)
    elif docopts["extract"]:
        extract_resources.main(args)
    elif docopts["add-book"]:
        manage_books.add_book(args)
    elif docopts["remove-book"]:
        manage_books.remove_book(args)
    elif docopts["list-books"]:
        manage_books.list_books(args)

    if docopts["-u"] or docopts["--update"]:
        create_pipeline.main(args)


if __name__ == '__main__':
    cli()
