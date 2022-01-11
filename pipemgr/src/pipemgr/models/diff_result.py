from typing import Callable, List, Generic, Optional, Set, TypeVar


T = TypeVar("T")


class DiffResult(Generic[T]):
    def __init__(self, before: Set[T], after: Set[T]):
        self.added: List[T] = []
        self.removed: List[T] = []

        diff = before ^ after

        for item in diff:
            if item in after:
                self.added.append(item)
            else:
                self.removed.append(item)

    @property
    def empty(self):
        return len(self.added) == 0 and len(self.removed) == 0

    def display_unified(self, formatter: Optional[Callable[[T], str]] = None):
        from itertools import chain

        if formatter is not None:
            added = map(formatter, self.added)
            removed = map(formatter, self.removed)
        else:
            added = map(str, self.added)
            removed = map(str, self.removed)

        unified = chain(
            map(lambda s: f"+ {s}", added),
            map(lambda s: f"- {s}", removed)
        )

        for output in sorted(unified):
            print(output)
