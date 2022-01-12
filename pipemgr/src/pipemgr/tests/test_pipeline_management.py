import shutil
import unittest
from typing import List, Union
from pathlib import Path

import pipemgr
from pydantic import BaseModel
from pipemgr.concourse.utils import expect
from pipemgr.models import Args, OSBook
from pipemgr.utils import read_yml


def setup_imports():
    global create_pipeline, manage_books, osbook_utils, extract_resources

    pipemgr.OUTPUT_ROOT = Path(__file__).parent/"out"
    if pipemgr.OUTPUT_ROOT.exists():
        # Start each test fresh
        shutil.rmtree(pipemgr.OUTPUT_ROOT)
    pipemgr.OUTPUT_ROOT.mkdir(parents=True)

    from pipemgr import create_pipeline, manage_books, osbook_utils, \
        extract_resources


setup_imports()

PIPELINE_PATH = pipemgr.OUTPUT_ROOT/"pipeline.yml"

# Test the CLI and the underlying functionality at the same time.
MNG_BOOK1 = Args(
    None,
    PIPELINE_PATH,
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
    PIPELINE_PATH,
    None,
    False,
    None,
    "",
    False
)

MY_BOOK = OSBook(expect(MNG_BOOK1.book, "Expected book repo"), MNG_BOOK1.server)
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
        self.assertTrue(PIPELINE_PATH.exists())

    def test_d_book_extract(self):
        osbook_utils.OSBOOKS_FILE.rename(
            osbook_utils.OSBOOKS_FILE.with_suffix(".dis"))
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
            PipelineValidator(**read_yml(PIPELINE_PATH))
        except FileNotFoundError:
            self.fail("Pipeline was not created")
        except Exception:
            self.fail("Pipeline was not valid yaml")

    def test_g_book_no_diff(self):
        pipeline_a = read_yml(PIPELINE_PATH)
        pipeline_b = read_yml(PIPELINE_PATH)
        self.assertEqual(manage_books.get_books_diff(pipeline_a, pipeline_b).empty, True)

    def test_h_book_with_diff(self):
        pipeline_a = read_yml(PIPELINE_PATH)
        pipeline_b = read_yml(PIPELINE_PATH)
        pipeline_b["resources"] = []
        self.assertEqual(manage_books.get_books_diff(pipeline_a, pipeline_b).empty, False)
