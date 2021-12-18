from typing import Optional, Union
from pathlib import Path


class DiskTokenCache:
    def __init__(self, location: Union[Path, str]) -> None:
        super().__init__()
        self.location = Path(location)
        self._token: Optional[str] = None

    def put_token(self, token: str):
        with open(self.location, "w") as fout:
            fout.write(token)
        self._token = token

    def get_token(self) -> Optional[str]:
        if self._token is not None:
            return self._token
        if not self.location.exists():
            return None
        with open(self.location, "r") as fin:
            token = fin.readline()
        return token
