import os
import re
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
from requests.sessions import Session

load_dotenv()

concourse_url = "https://concourse-v7.openstax.org"
concourse_login = f"{concourse_url}/sky/login"
pipeline_url = f"{concourse_url}/api/v1/teams/CE/pipelines"


@contextmanager
def _login() -> Generator[Session, None, None]:
    username = os.environ["CONCOURSE_USERNAME"]
    password = os.environ["CONCOURSE_PASSWORD"]

    ldap_url_regex = re.compile(r"\/sky\/issuer\/auth\/ldap\?req=[a-z0-9]+")
    bearer_regex = re.compile('authToken: "bearer (.+)"')

    with Session() as session:
        r = session.get(concourse_login)

        ldap_url = re.search(ldap_url_regex, r.text).group(0)
        ldap_login_url = f"{concourse_url}{ldap_url}"

        data = {"login": username, "password": password}

        r = session.post(ldap_login_url, data=data)

        token = re.search(bearer_regex, r.text).group(1)

        session.headers = {"Authorization": f"Bearer {token}"}

        yield session


def get_pipeline(pipeline: str):
    pipeline_config_url = f"{pipeline_url}/{pipeline}/config"

    with _login() as session:
        return session.get(pipeline_config_url).json()


def set_pipeline(pipeline: str, config: dict):
    pipeline_config_url = f"{pipeline_url}/{pipeline}/config"

    with _login() as session:
        session.put(pipeline_config_url, data=config)
