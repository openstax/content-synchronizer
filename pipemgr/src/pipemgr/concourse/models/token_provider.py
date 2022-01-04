from typing import Protocol

from httpx import Client


class TokenProvider(Protocol):
    def get_token(self, session: Client, force_new: bool, concourse_url: str) -> str:
        """Get a token from the provider regardless of its activation status"""
        raise NotImplementedError()
