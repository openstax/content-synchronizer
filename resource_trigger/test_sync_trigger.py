"""Tests for Concourse (Pipeline Trigger) Resource"""
from src import check
import pytest
import io
import json


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


def test_version_format(mocker):

    sync_file = """
        college-algebra col11759
        precalculus col11667
        algebra-and-trigonometry col11758
        precalculus-coreq col32026
        """

    mocker.patch(
        'src.check.get_sync_file',
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
        'src.check.get_sync_file',
        return_value=sync_file
    )

    instream = fake_input_stream()
    assert isinstance(check._check(instream), list) == True
