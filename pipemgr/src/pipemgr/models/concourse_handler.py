from typing import Tuple

from ..concourse.models import Session, LDAPTokenProvider, DiskTokenCache
from ..concourse.utils import expect
from .. import OUTPUT_ROOT


CONCOURSE_URL = "https://concourse-v7.openstax.org"
PIPELINE_URL = f"{CONCOURSE_URL}/api/v1/teams/CE/pipelines"
PIPELINE_CONFIG_URL = f"{PIPELINE_URL}/{{pipeline}}/config"


class ConcourseHandler:
    """Composite, Singleton class for controlling concourse

    Use .get() to get an instance
    """
    __instance = None

    def __init__(self):
        self._session = Session(
            CONCOURSE_URL,
            LDAPTokenProvider(DiskTokenCache(OUTPUT_ROOT/"token.txt"))
        )

    @property
    def connection(self):
        return self._session.get_connection(False)

    @property
    def concourse_url(self):
        return CONCOURSE_URL

    def close(self):
        self._session.close()

    def get_pipeline(self, pipeline: str) -> Tuple[dict, str]:
        conn = self.connection
        r = conn.get(PIPELINE_CONFIG_URL.format(pipeline=pipeline))
        r.raise_for_status()
        pipeline_version = expect(
            r.headers.get("X-Concourse-Config-Version"),
            "BUG: X-Concourse-Config-Version not found"
        )
        pipeline_cfg = r.json()["config"]
        return (pipeline_cfg, pipeline_version)

    def set_pipeline(self, pipeline: str, config: dict, pipeline_version: str):
        import json
        conn = self.connection
        headers = {"Content-Type": "application/json",
                   "X-Concourse-Config-Version": pipeline_version}
        r = conn.put(
            PIPELINE_CONFIG_URL.format(pipeline=pipeline),
            data=json.dumps(config),
            headers=headers
        )
        r.raise_for_status()

    @staticmethod
    def get():
        if ConcourseHandler.__instance is None:
            ConcourseHandler.__instance = ConcourseHandler()
        return ConcourseHandler.__instance
