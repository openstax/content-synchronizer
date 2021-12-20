from typing import Protocol

from requests.sessions import Session


class TokenProvider(Protocol):
    def get_token(self, session: Session, force_new: bool, concourse_url: str) -> str:
        """Get a token from the provider regardless of its activation status"""
        raise NotImplementedError()
