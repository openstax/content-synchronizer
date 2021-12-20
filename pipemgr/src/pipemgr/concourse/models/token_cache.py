from typing import Protocol, Optional


class TokenCache(Protocol):
    def get_token(self) -> Optional[str]:
        """Get a token from the cache"""

    def put_token(self, token: str):
        """Put a token in the cache"""
