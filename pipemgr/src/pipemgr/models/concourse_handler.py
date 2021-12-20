import logging

from ..concourse.models import Session, LDAPTokenProvider, DiskTokenCache
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

    def get_pipeline(self, pipeline: str) -> dict:
        pipeline_cfg = {}
        try:
            conn = self.connection
            pipeline_cfg = conn.get(
                PIPELINE_CONFIG_URL.format(pipeline=pipeline)).json()["config"]
        except Exception as e:
            logging.error(e)
        return pipeline_cfg

    def set_pipeline(self, pipeline: str, config: dict):
        conn = self.connection
        conn.put(PIPELINE_CONFIG_URL.format(pipeline=pipeline, data=config))

    @staticmethod
    def get():
        if ConcourseHandler.__instance is None:
            ConcourseHandler.__instance = ConcourseHandler()
        return ConcourseHandler.__instance
