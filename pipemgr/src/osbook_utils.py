from pathlib import Path
from typing import Optional, Set

from .utils import read_yml, write_yml
from . import OUTPUT_ROOT
from .models import OSBook

OSBOOKS_FILE = OUTPUT_ROOT/"osbooks.yml"


def read_osbooks(osbooks_path: Optional[Path] = None) -> Set[OSBook]:
    if osbooks_path is None:
        osbooks_path = OSBOOKS_FILE
    if not osbooks_path.exists():
        return set()
    return set(
        OSBook.from_osbook_collection(book)
        for book in read_yml(osbooks_path)
    )


def write_osbooks(osbooks: Set[OSBook], osbooks_path: Optional[Path] = None):
    if osbooks_path is None:
        osbooks_path = OSBOOKS_FILE
    write_yml([osbook.dict() for osbook in osbooks], osbooks_path)
