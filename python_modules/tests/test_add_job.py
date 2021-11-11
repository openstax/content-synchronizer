import shutil
import unittest
from typing import List, Union

import python_modules
python_modules.OUTPUT_ROOT = python_modules.OUTPUT_ROOT/"test"
if not python_modules.OUTPUT_ROOT.exists():
    python_modules.OUTPUT_ROOT.mkdir()
else:
    shutil.rmtree(python_modules.OUTPUT_ROOT)
    python_modules.OUTPUT_ROOT.mkdir()

from python_modules import create_pipeline, manage_books, osbook_utils, extract_resources
from python_modules.models import Args
from python_modules.utils import read_yml

from pydantic import BaseModel

PIPELINE = python_modules.OUTPUT_ROOT/"pipeline.yml"

# Test the CLI and the underlying functionality at the same time.
MNG_BOOK1 = Args(
    None,
    None,
    False,
    "TEST",
    "example.com",
    True
)

MNG_BOOK2 = Args(
    None,
    None,
    False,
    "OTHER",
    "example.com",
    True
)

EXTRACT_RES = Args(
    PIPELINE,
    None,
    False,
    None,
    "",
    False
)

MY_BOOK = osbook_utils.OSBook(MNG_BOOK1.book, MNG_BOOK1.server)
books_added = 0

class Resource(BaseModel):
    name: str
    type: str
    source: dict

class BookResSource(BaseModel):
    branch: str
    uri: str
    private_key: str

class BookResource(Resource):
    source: BookResSource

class ArchiveResSource(BaseModel):
    archive_server: str
    book_repo: str
    github_token: str

class ArchiveResource(Resource):
    source: ArchiveResSource

class PipelineValidator(BaseModel):
    resource_types: List[Resource]
    resources: List[Union[BookResource, ArchiveResource]]
    jobs: List[dict]

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
        _add_book(MNG_BOOK1)
        _add_book(MNG_BOOK2)
        self.assertTrue(osbook_utils.OSBOOKS_FILE.exists())

    def test_b_load_book(self):
        osbooks = osbook_utils.read_osbooks()
        self.assertTrue(MY_BOOK in osbooks)
        self.assertEqual(books_added, len(osbooks))

    def test_c_create_pipeline(self):
        create_pipeline.main(MNG_BOOK1)
        self.assertTrue(PIPELINE.exists())

    def test_d_book_extract(self):
        osbook_utils.OSBOOKS_FILE.rename(osbook_utils.OSBOOKS_FILE.with_suffix(".dis"))
        # Extracting from the same pipeline should be idempotent
        for _ in range(5):
            extract_resources.main(EXTRACT_RES)
        osbooks = osbook_utils.read_osbooks()
        self.assertTrue(MY_BOOK in osbooks)
        self.assertEqual(books_added, len(osbooks))

    def test_e_book_delete(self):
        _remove_book(MNG_BOOK1)
        osbooks = osbook_utils.read_osbooks()
        self.assertEqual(books_added, len(osbooks))
        self.assertTrue(MY_BOOK not in osbooks)
        create_pipeline.main(MNG_BOOK1)

    def test_f_pipeline_valid_yaml(self):
        try:
            PipelineValidator(**read_yml(PIPELINE))
        except FileNotFoundError:
            self.fail("Pipeline was not created")
        except:
            self.fail("Pipeline was not valid yaml")
