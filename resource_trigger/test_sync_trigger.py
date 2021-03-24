"""Tests for Concourse (Pipeline Trigger) Resource"""
import check
import pytest
import io
import json
import requests
from utils import BOOK_UUIDS, determine_archive_server


def fake_input_stream():
    def make_stream(json_obj):
        stream = io.StringIO()
        json.dump(json_obj, stream)
        stream.seek(0)
        return stream

    def make_input():
        return {
            "source": {
                "archive_server": "qa.cnx.org",
                "book_repo": "osbooks-college-algebra-bundle",
                "github_token": "xxxx"
            },
            "version": ""
        }

    return make_stream(make_input())


def test_server_resolution():
    server = 'qa.cnx.org'
    expected_server = determine_archive_server(server)
    assert expected_server == 'archive-qa.cnx.org'

    server = 'staging.cnx.org'
    expected_server = determine_archive_server(server)
    assert expected_server == 'archive-staging.cnx.org'

    server = 'cnx.org'
    expected_server = determine_archive_server(server)
    assert expected_server == 'archive.cnx.org'

    server = 'qa'
    expected_server = determine_archive_server(server)
    assert expected_server == 'archive-qa.cnx.org'

    server = 'prod'
    expected_server = determine_archive_server(server)
    assert expected_server == 'archive.cnx.org'

    server = 'staging'
    expected_server = determine_archive_server(server)
    assert expected_server == 'archive-staging.cnx.org'

    server = ''
    with pytest.raises(SystemExit):
        determine_archive_server(server)


def test_github_request(requests_mock):
    token = 'fake-token-xxxx'
    repo = 'osbooks-college-algebra-bundle'
    sync_file = """
    college-algebra col11759
    """
    content_encoded = sync_file.encode('utf-8')
    link = f"https://raw.githubusercontent.com/openstax/{repo}/main/archive-syncfile"
    boop = requests_mock.get(link, content=content_encoded)
    decoded_sync_file = check.get_sync_file(token, repo)
    assert decoded_sync_file == sync_file


def test_archive_request(mocker, requests_mock):
    uuid = BOOK_UUIDS['col11759']
    sync_file = """
    college-algebra col11759
    """
    mocker.patch(
        'check.get_sync_file',
        return_value=sync_file
    )
    instream = fake_input_stream()
    content = json.dumps({'headVersion': '6.5'})
    content_encoded = content.encode('utf-8')
    link = f"https://archive-qa.cnx.org/extras/{uuid}"
    requests_mock.get(link, content=content_encoded)
    versions = check._check(instream)[0]['versions']
    assert versions == 'col11759@6.5'


def test_version_format(mocker):

    sync_file = """
        college-algebra col11759
        precalculus col11667
        algebra-and-trigonometry col11758
        precalculus-coreq col32026
        """

    mocker.patch(
        'check.get_sync_file',
        return_value=sync_file
    )

    instream = fake_input_stream()
    versions = check._check(instream)[0]['versions']
    number_of_actual_versions = len(versions.split(','))
    number_of_expected_versions = 4
    assert number_of_expected_versions == number_of_actual_versions


def test_check_type(mocker):

    sync_file = """
        college-algebra col11759
        precalculus col11667
        algebra-and-trigonometry col11758
        precalculus-coreq col32026
        """

    mocker.patch(
        'check.get_sync_file',
        return_value=sync_file
    )

    instream = fake_input_stream()
    assert isinstance(check._check(instream), list) == True
