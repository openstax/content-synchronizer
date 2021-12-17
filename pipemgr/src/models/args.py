from pathlib import Path
from typing import NamedTuple, Optional


def _resolve_path(path: Optional[str]) -> Optional[Path]:
    if path is not None:
        return Path(path).resolve()


class Args(NamedTuple):
    file: Optional[Path]
    outfile: Optional[Path]
    clean: bool
    book: Optional[str]
    server: str
    yes: bool = False
    repo_only: bool = False

    @staticmethod
    def from_docopts(docopts: dict) -> "Args":
        return Args(
            _resolve_path(docopts["--file"] or docopts["-f"]),
            _resolve_path(docopts["--output"] or docopts["-o"]),
            docopts["--clean"] or docopts["-c"],
            docopts["BOOK"],
            docopts["--server"],
            docopts["-y"] or docopts["--yes"],
            docopts["-r"] or docopts["--repo-only"]
        )
