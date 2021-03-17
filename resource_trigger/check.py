#!/usr/bin/env python3
import requests
import json
import sys

from utils import msg, parse_legacy_ids, determine_archive_server, BOOK_UUIDS


def _check(instream):
    payload = json.load(instream)
    source = payload['source']
    token = source['github_token']
    repo = source['book_repo']
    server = source.get('archive_server')
    archive_server = determine_archive_server(server)

    msg(f"Syncing {repo} with {archive_server}...")

    headers = {'Authorization': 'token ' + token}
    endpoint = f"https://raw.githubusercontent.com/openstax/{repo}/main/archive-syncfile"
    resp = requests.get(endpoint, headers=headers)

    if resp.status_code != 200:
        msg(f"Error: Unable to get archive-syncfile for {repo}")
        sys.exit(1)

    sync_file = resp.content.decode()
    legacy_ids = parse_legacy_ids(sync_file)

    # Get versions from uuid via archive api
    versions = []
    for legacy_id in legacy_ids:
        try:
            uuid = BOOK_UUIDS[legacy_id]
        except KeyError as error:
            msg(error, file=sys.stderr)
            sys.exit(1)
        link = f"https://{archive_server}/contents/{uuid}"
        resp = requests.get(link)

        if resp.status_code != 200:
            msg(f"Error: Unable to get version for {uuid}")
            sys.exit(1)

        content = json.loads(resp.content)
        version = content['version']
        legacy_id = content['legacy_id']
        versions.append(f'{legacy_id}@{version}')

    return [{"versions": ','.join(versions)}]


def main():
    print(json.dumps(_check(sys.stdin)))


if __name__ == '__main__':
    main()
