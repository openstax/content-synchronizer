from pathlib import Path
import shutil
import unittest

import python_modules
python_modules.OUTPUT_ROOT = python_modules.OUTPUT_ROOT/"test"
if not python_modules.OUTPUT_ROOT.exists():
    python_modules.OUTPUT_ROOT.mkdir()
else:
    shutil.rmtree(python_modules.OUTPUT_ROOT)
    python_modules.OUTPUT_ROOT.mkdir()

from python_modules import create_pipeline, manage_books, osbook_utils, extract_resources
from python_modules.models import Args, args
from python_modules.utils import read_yml

# TODO: It would be better to include a schema for the pipeline as well

PIPELINE = python_modules.OUTPUT_ROOT/"pipeline.yml"

# Test the CLI and the underlying functionality at the same time.
mng_book1 = Args(
    None,
    None,
    False,
    "TEST",
    "example.com",
    True
)

mng_book2 = Args(
    None,
    None,
    False,
    "OTHER",
    "example.com",
    True
)

extract_res = Args(
    PIPELINE,
    None,
    False,
    None,
    "",
    False
)

MY_BOOK = osbook_utils.OSBook(mng_book1.book, mng_book1.server)
books_added = 0

def _add_book(args):
    global books_added
    books_added += 1
    manage_books.add_book(args)

def _remove_book(args):
    global books_added
    books_added -= 1
    manage_books.remove_book(args)

class TestAddJob(unittest.TestCase):

    def test_a_add_book(self):
        _add_book(mng_book1)
        _add_book(mng_book2)
        self.assertTrue(osbook_utils.OSBOOKS_FILE.exists())

    def test_b_load_book(self):
        osbooks = osbook_utils.read_osbooks()
        self.assertTrue(MY_BOOK in osbooks)
        self.assertEqual(books_added, len(osbooks))

    def test_c_create_pipeline(self):
        create_pipeline.main(mng_book1)
        self.assertTrue(PIPELINE.exists())

    def test_d_book_extract(self):
        osbook_utils.OSBOOKS_FILE.rename(osbook_utils.OSBOOKS_FILE.with_suffix(".dis"))
        # Extracting from the same pipeline should be idempotent
        for _ in range(5):
            extract_resources.main(extract_res)
        osbooks = osbook_utils.read_osbooks()
        self.assertTrue(MY_BOOK in osbooks)
        self.assertEqual(books_added, len(osbooks))

    def test_e_book_delete(self):
        _remove_book(mng_book1)
        osbooks = osbook_utils.read_osbooks()
        self.assertEqual(books_added, len(osbooks))
        self.assertTrue(MY_BOOK not in osbooks)
        create_pipeline.main(mng_book1)

    def test_f_pipeline_valid_yaml(self):
        try:
            read_yml(PIPELINE)
        except FileNotFoundError:
            self.fail("Pipeline was not created")
        except:
            self.fail("Pipeline was not valid yaml")

if __name__ == "__main__":
    unittest.main().main()