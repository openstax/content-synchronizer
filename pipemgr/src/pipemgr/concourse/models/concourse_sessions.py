import logging
from contextlib import contextmanager
from typing import Callable, Generator, Tuple

import httpx
from httpx import Client, Response

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
        self._client = None

    @property
    def is_open(self):
        return self._client is not None

    @property
    def client(self):
        if self._client is None:
            self._client = Client()
            self._update_token(self._client, False)
        return self._client

    def _make_request(self, make_request: Callable[[Client], Response]) -> Response:
        client = self.client
        for _ in range(2):
            r = make_request(client)
            if r.status_code == httpx.codes.UNAUTHORIZED:
                logging.warning(
                    f"Got {r.status_code} when trying to access {self.concourse_url}"
                )
                client.headers.update({"Authorization": ""})
                self._update_token(client, True)
            else:
                return r
        raise Exception("Could not connect to concourse server")

    def _build_url(self, *args) -> str:
        parts = [self.concourse_url]
        parts.extend(str(p) for p in args)
        return '/'.join(parts)

    def _build_teams_url(self, *args):
        return self._build_url("api", "v1", "teams", *args)

    def _build_pipeline_url(self, team: str, pipeline: str):
        return self._build_teams_url(team, "pipelines", pipeline, "config")

    def _update_token(self, client: Client, force_new: bool):
        token = self._token_provider.get_token(
            client, force_new, self.concourse_url
        )
        client.headers.update({"Authorization": f"bearer {token}"})

    def close(self):
        if self._client is None:
            return
        try:
            self._client.close()
        except Exception as e:
            logging.error(e)
        finally:
            self._client = None

    def get_pipeline(self, team: str, pipeline: str) -> Tuple[dict, str]:
        r = self._make_request(
            lambda c: c.get(self._build_pipeline_url(team, pipeline))
        )
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
        headers = {"X-Concourse-Config-Version": pipeline_version}
        # https://github.com/concourse/concourse/blob/d55be66cc6b10101a8b4ddd9122e437cb10ccf52/go-concourse/concourse/configs.go#L76
        r = self._make_request(
            lambda c: c.put(
                self._build_pipeline_url(team, pipeline),
                json=config,
                headers=headers
            )
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
