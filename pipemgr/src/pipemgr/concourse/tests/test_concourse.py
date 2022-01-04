from unittest.mock import MagicMock

import pipemgr.concourse.models.concourse_sessions as concourse_sessions
from pipemgr.concourse.models import (DiskTokenCache, LDAPTokenProvider,
                                      ldap_token_provider)

# TODO: These tests could be better:
# Check that tokens are only tried twice before an exception is raised


class MockResponse:
    def __init__(self):
        self.token = ""

    @property
    def text(self):
        return f"bearer {self.token}"

    @property
    def status_code(self):
        return (
            200
            if self.token == "bearer 1234" else
            401
        )


class MockSession:
    def __init__(self):
        self.headers = {}
        self.mock_response = MockResponse()

    def get(self, url: str):
        self.mock_response.token = self.headers.get("Authorization", "")
        return self.mock_response

    def post(self, url: str, data: dict):
        return self.mock_response


def mock_get_token(session: MockSession, force_new: bool, concourse_url: str):
    return (
        "65483965"
        if not force_new else
        "1234"
    )


def test_session_retry():
    """Check that the session will attempt to get a new token if the first one fails"""
    concourse_sessions.Session = MockSession

    LDAPTokenProvider.get_token = MagicMock(side_effect=mock_get_token)
    token_provider = LDAPTokenProvider(DiskTokenCache("NEVER_USED"))
    my_session = concourse_sessions.ConcourseSession(
        "NEVER_USED",
        token_provider
    )
    _ = my_session.connection
    LDAPTokenProvider.get_token.assert_any_call(
        my_session._session, False, "NEVER_USED")
    LDAPTokenProvider.get_token.assert_any_call(
        my_session._session, True, "NEVER_USED")
    assert LDAPTokenProvider.get_token.call_count == 2
    assert my_session.is_open


def test_disk_cache():
    import shutil
    from pathlib import Path

    output_dir = Path(__file__).parent/"out"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()

    cache_path = output_dir/"token.txt"
    cache = DiskTokenCache(cache_path)

    assert cache.get_token() is None

    cache.put_token("TESTING")
    assert cache_path.exists()
    assert cache.get_token() == "TESTING"


def test_ldap_regex():
    import re

    bearer_re = ldap_token_provider._BEARER_REGEX

    msg = 'authToken: "bearer tokenAAA"'
    result = re.search(bearer_re, msg)
    assert result is not None
    assert result.group(1) == "tokenAAA"

    msg = 'authToken: "Bearer tokenAAA"'
    result = re.search(bearer_re, msg)
    assert result is not None
    assert result.group(1) == "tokenAAA"
