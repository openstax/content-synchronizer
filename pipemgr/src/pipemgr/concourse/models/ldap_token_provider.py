import re
from getpass import getpass
from typing import Optional

from requests.sessions import Session
from .token_cache import TokenCache
from ..utils import expect

_LDAP_URL_REGEX = re.compile(r"\/sky\/issuer\/auth\/ldap\?req=[a-z0-9]+")
_BEARER_REGEX = re.compile('authToken: "[Bb]earer (.+)"')


class LDAPTokenProvider():
    def __init__(self, token_cache: TokenCache):
        self._token: Optional[str] = None
        self._token_cache = token_cache

    def _get_token(self, session: Session, concourse_url: str) -> str:
        concourse_login = f"{concourse_url}/sky/login"

        r = session.get(concourse_login)

        ldap_url = expect(
            re.search(_LDAP_URL_REGEX, r.text),
            "BUG: no ldap url found"
        ).group(0)

        ldap_login_url = f"{concourse_url}{ldap_url}"

        print("Concourse login")
        username = input("Username: ")
        password = getpass()

        data = {"login": username, "password": password}

        r = session.post(ldap_login_url, data=data)

        token = expect(
            re.search(_BEARER_REGEX, r.text),
            "BUG: no bearer found"
        ).group(1)

        return token

    def get_token(self, session: Session, force_new: bool, concourse_url: str) -> str:
        token: Optional[str] = None
        if not force_new:
            token = self._token_cache.get_token()
        if token is None:
            token = self._get_token(session, concourse_url)
            self._token_cache.put_token(token)
        return token
