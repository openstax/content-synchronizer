from unittest.mock import MagicMock

from pipemgr.concourse.models import session
from pipemgr.concourse.models import LDAPTokenProvider, DiskTokenCache


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


def test_session():
    session.RequestsSession = MockSession

    LDAPTokenProvider.get_token = MagicMock(side_effect=mock_get_token)
    token_provider = LDAPTokenProvider(DiskTokenCache("NEVER_USED"))
    my_session = session.Session(
        "NEVER_USED",
        token_provider
    )
    my_session.get_connection(False)
    assert LDAPTokenProvider.get_token.call_count == 2
    assert my_session.is_open
