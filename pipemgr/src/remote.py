import logging
import os
import re
from contextlib import contextmanager
from typing import Generator
from getpass import getpass

from dotenv import load_dotenv
from requests.sessions import Session

load_dotenv('./.env')

concourse_url = "https://concourse-v7.openstax.org"
concourse_login = f"{concourse_url}/sky/login"
pipeline_url = f"{concourse_url}/api/v1/teams/CE/pipelines"
pipeline_config_url = f"{pipeline_url}/{{pipeline}}/config"


@contextmanager
def _login() -> Generator[Session, None, None]:
    username = os.environ.get("CONCOURSE_USERNAME", input("Username: "))
    password = os.environ.get("CONCOURSE_PASSWORD", getpass())

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


def get_pipeline(pipeline: str) -> dict:
    pipeline_cfg = {}
    try:
        with _login() as session:
            pipeline_cfg = session.get(
                pipeline_config_url.format(pipeline=pipeline)).json()["config"]
    except Exception as e:
        logging.error(e)

    return pipeline_cfg


def set_pipeline(pipeline: str, config: dict):
    with _login() as session:
        session.put(pipeline_config_url.format(pipeline=pipeline), data=config)
