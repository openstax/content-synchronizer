from typing import NamedTuple, Optional

class Args(NamedTuple):
    file: Optional[str]
    clean: bool
    book: str
    server: str
    yes: bool = False

    @staticmethod
    def from_docopts(docopts: dict) -> "Args":
        return Args(
            docopts["--file"] or docopts["-f"],
            docopts["--clean"] or docopts["-c"],
            docopts["BOOK"],
            docopts["--server"],
            docopts["-y"] or docopts["--yes"]
        )