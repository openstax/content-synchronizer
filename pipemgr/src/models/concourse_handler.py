import logging

from src.concourse.models import Session, LDAPTokenProvider, DiskTokenCache
from src import OUTPUT_ROOT


concourse_url = "https://concourse-v7.openstax.org"
pipeline_url = f"{concourse_url}/api/v1/teams/CE/pipelines"
pipeline_config_url = f"{pipeline_url}/{{pipeline}}/config"


class ConcourseHandler:
    """Composite, Singleton class for controlling concourse

    Use .get() to get an instance
    """
    __instance = None

    def __init__(self) -> None:
        self._session = Session(
            concourse_url,
            LDAPTokenProvider(DiskTokenCache(OUTPUT_ROOT/"token.txt"))
        )

    @property
    def connection(self):
        return self._session.get_connection(False)

    @property
    def concourse_url(self):
        return concourse_url

    def close(self):
        self._session.close()

    def get_pipeline(self, pipeline: str) -> dict:
        pipeline_cfg = {}
        try:
            conn = self.connection
            pipeline_cfg = conn.get(
                pipeline_config_url.format(pipeline=pipeline)).json()["config"]
        except Exception as e:
            logging.error(e)
        return pipeline_cfg

    def set_pipeline(self, pipeline: str, config: dict):
        conn = self.connection
        conn.put(pipeline_config_url.format(pipeline=pipeline, data=config))

    @staticmethod
    def get():
        if ConcourseHandler.__instance is None:
            ConcourseHandler.__instance = ConcourseHandler()
        return ConcourseHandler.__instance
