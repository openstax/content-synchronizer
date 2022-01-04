import logging
from contextlib import contextmanager
from typing import Generator, Tuple

import httpx
from httpx import Client

from ..utils import expect
from .token_provider import TokenProvider


class ConcourseSession:
    def __init__(
        self,
        concourse_url: str,
        token_provider: TokenProvider
    ):
        self.concourse_url = concourse_url
        self._token_provider = token_provider
        self._session = None

    @property
    def is_open(self):
        return self._session is not None

    @property
    def connection(self):
        if self._session is None:
            self._session = self._login()
        return self._session

    def _build_url(self, *args) -> str:
        parts = [self.concourse_url]
        parts.extend(str(p) for p in args)
        return '/'.join(parts)

    def _build_teams_url(self, *args):
        return self._build_url("api", "v1", "teams", *args)

    def _build_pipeline_url(self, team: str, pipeline: str):
        return self._build_teams_url(team, "pipelines", pipeline, "config")

    def _test_token(self, session: Client):
        teams_url = self._build_teams_url()
        for i in range(2):
            r = session.get(teams_url)
            if r.status_code != httpx.codes.OK:
                logging.warning(
                    f"Got {r.status_code} when trying to access {teams_url}"
                )
                if i == 1:
                    raise Exception("Could not connect to concourse server")
                else:
                    session.headers.update({"Authorization": ""})
                    self._update_token(session, True)

    def _update_token(self, session: Client, force_new: bool):
        token = self._token_provider.get_token(
            session, force_new, self.concourse_url
        )
        session.headers.update({"Authorization": f"bearer {token}"})

    def _login(self) -> Client:
        self.close()  # close any connections that might be lingering
        session = Client()
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

    def get_pipeline(self, team: str, pipeline: str) -> Tuple[dict, str]:
        conn = self.connection
        r = conn.get(self._build_pipeline_url(team, pipeline))
        # https://github.com/concourse/concourse/blob/d55be66cc6b10101a8b4ddd9122e437cb10ccf52/go-concourse/concourse/configs.go#L40
        if r.status_code == 404:
            return ({}, "")
        r.raise_for_status()
        pipeline_version = expect(
            r.headers.get("X-Concourse-Config-Version"),
            "BUG: X-Concourse-Config-Version not found"
        )
        pipeline_cfg = r.json()["config"]
        return (pipeline_cfg, pipeline_version)

    def set_pipeline(
        self,
        team: str,
        pipeline: str,
        config: dict,
        pipeline_version: str
    ):
        conn = self.connection
        # https://github.com/concourse/concourse/blob/d55be66cc6b10101a8b4ddd9122e437cb10ccf52/go-concourse/concourse/configs.go#L76
        headers = {"X-Concourse-Config-Version": pipeline_version}
        r = conn.put(
            self._build_pipeline_url(team, pipeline),
            json=config,
            headers=headers
        )
        r.raise_for_status()


@contextmanager
def concourse_session(
    concourse_url: str,
    token_provider: TokenProvider
) -> Generator[ConcourseSession, None, None]:
    c_session = ConcourseSession(concourse_url, token_provider)
    try:
        yield c_session
    finally:
        c_session.close()
