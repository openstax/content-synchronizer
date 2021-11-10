import os
from pathlib import Path
import shutil
import unittest
from typing import NamedTuple

import python_modules
python_modules.OUTPUT_ROOT = python_modules.OUTPUT_ROOT/"test"
if not python_modules.OUTPUT_ROOT.exists():
    python_modules.OUTPUT_ROOT.mkdir()
else:
    shutil.rmtree(python_modules.OUTPUT_ROOT)
    python_modules.OUTPUT_ROOT.mkdir()

from python_modules import create_pipeline, manage_books, osbook_utils, extract_resources
from python_modules.utils import read_yml

PIPELINE = python_modules.OUTPUT_ROOT/"pipeline.yml"

class Args(NamedTuple):
    book: str
    server: str = "TESTING.org"
    update: bool = False
    clean: bool = False
    yes: bool = True
    file: Path = PIPELINE

mybook = osbook_utils.OSBook("TEST_BOOK", "TESTING.org")
BOOKS_ADDED = 0

def _add_book(args):
    global BOOKS_ADDED
    BOOKS_ADDED += 1
    manage_books.add_book(args)

def _remove_book(args):
    global BOOKS_ADDED
    BOOKS_ADDED -= 1
    manage_books.remove_book(args)

class TestAddJob(unittest.TestCase):

    def test_a_add_book(self):
        _add_book(Args(mybook.book_repo, mybook.archive_server))
        _add_book(Args("OTHER_BOOK"))
        self.assertTrue(osbook_utils.OSBOOKS_FILE.exists())

    def test_b_load_book(self):
        osbooks = osbook_utils.read_osbooks()
        self.assertTrue(mybook in osbooks)
        self.assertEqual(BOOKS_ADDED, len(osbooks))

    def test_c_create_pipeline(self):
        create_pipeline.main(Args(""))
        self.assertTrue(PIPELINE.exists())

    def test_d_book_extract(self):
        osbook_utils.OSBOOKS_FILE.rename(osbook_utils.OSBOOKS_FILE.with_suffix(".dis"))
        # Extracting from the same pipeline should be idempotent
        for _ in range(5):
            extract_resources.main(Args(""))
        osbooks = osbook_utils.read_osbooks()
        self.assertTrue(mybook in osbooks)
        self.assertEqual(BOOKS_ADDED, len(osbooks))

    def test_e_book_delete(self):
        _remove_book(Args(mybook.book_repo, mybook.archive_server))
        osbooks = osbook_utils.read_osbooks()
        self.assertEqual(BOOKS_ADDED, len(osbooks))
        self.assertTrue(mybook not in osbooks)

if __name__ == "__main__":
    unittest.main().main()