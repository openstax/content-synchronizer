from typing import List, NamedTuple

from .osbook import OSBook


class DiffResult(NamedTuple):
    added: List[OSBook]
    removed: List[OSBook]

    @property
    def empty(self):
        return len(self.added) == 0 and len(self.removed) == 0
