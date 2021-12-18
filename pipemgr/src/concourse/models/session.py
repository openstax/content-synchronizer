import logging
from typing import Optional
import requests
from requests.sessions import Session as RequestsSession
from .token_provider import TokenProvider


class Session:
    def __init__(
        self,
        concourse_url: str,
        token_provider: TokenProvider,
        session: Optional[RequestsSession] = None
    ) -> None:
        self.concourse_url = concourse_url
        self._token_provider = token_provider
        self._session = session

    def _test_token(self, session: RequestsSession):
        teams_url = f"{self.concourse_url}/api/v1/teams"
        for i in range(2):
            r = session.get(teams_url)
            if r.status_code != requests.codes.ok:
                logging.warning(
                    f"Got {r.status_code} when trying to access {teams_url}"
                )
                if i == 1:
                    raise Exception("Could not connect to concourse server")
                else:
                    session.headers.update({"Authorization": ""})
                    self._update_token(session, True)

    def _update_token(self, session: RequestsSession, force_new: bool):
        token = self._token_provider.get_token(
            session, force_new, self.concourse_url
        )
        session.headers.update({"Authorization": f"bearer {token}"})

    def _login(self) -> RequestsSession:
        self.close()  # close any connections that might be lingering
        session = RequestsSession()
        self._update_token(session, False)
        self._test_token(session)
        return session

    def close(self):
        if self._session is None:
            return
        try:
            self._session.close()
        except Exception as e:
            logging.error(e)
        finally:
            self._session = None

    def get_connection(self, force_new: bool) -> RequestsSession:
        if self._session is None or force_new:
            self._session = self._login()
        return self._session
