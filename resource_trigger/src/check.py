#!/usr/bin/env python3
import requests
import json
import sys

from src.utils import msg, parse_legacy_ids, determine_archive_server, BOOK_UUIDS


def get_sync_file(token, repo):
    headers = {'Authorization': 'token ' + token}
    endpoint = f"https://raw.githubusercontent.com/openstax/{repo}/main/archive-syncfile"
    resp = requests.get(endpoint, headers=headers)

    if resp.status_code != 200:
        msg(f"Error: Unable to get archive-syncfile for {repo}")
        sys.exit(1)

    sync_file = resp.content.decode()

    return sync_file


def get_content_version(archive_server, uuid):
    link = f"https://{archive_server}/contents/{uuid}"
    resp = requests.get(link)

    if resp.status_code != 200:
        msg(f"Error: Unable to get version for {uuid}")
        sys.exit(1)

    content = json.loads(resp.content)
    legacy_id = content['legacy_id']
    version = content['version']

    content_version = f'{legacy_id}@{version}'

    return content_version


def _check(instream):
    payload = json.load(instream)
    source = payload['source']
    token = source['github_token']
    repo = source['book_repo']
    server = source.get('archive_server')
    archive_server = determine_archive_server(server)

    msg(f"<<<< Payload: {payload} >>>>")
    msg(f"<<<< Syncing {repo} with {archive_server} >>>>")

    # Get uuid from legacy ids
    sync_file = get_sync_file(token, repo)
    legacy_ids = parse_legacy_ids(sync_file)

    msg(f"<<<< Getting versions for Legacy IDS: {legacy_ids} >>>>")

    # Get versions from uuid via archive api
    versions = []
    for legacy_id in legacy_ids:
        try:
            uuid = BOOK_UUIDS[legacy_id]
        except KeyError as error:
            msg(error, file=sys.stderr)
            sys.exit(1)

        version = get_content_version(archive_server, uuid)
        versions.append(version)

    return [{"versions": ','.join(versions)}]


def main():
    print(json.dumps(_check(sys.stdin)))


if __name__ == '__main__':
    main()
