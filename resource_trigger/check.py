#!/usr/bin/env python3
import requests
import json
import sys

from utils import msg, parse_legacy_ids, determine_archive_server, BOOK_UUIDS


def get_sync_file(token, repo):
    headers = {'Authorization': 'token ' + token}
    repository = f"https://raw.githubusercontent.com/openstax/{repo}/main"

    try:
        endpoint = f"{repository}/META-INF/books.xml"
        resp = requests.get(endpoint, headers=headers)
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        try:
            endpoint = f"{repository}/archive-syncfile"
            resp = requests.get(endpoint, headers=headers)
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            msg("Error: missing '/META-INF/books.xml' or 'archive-syncfile' from {}", repo)
            sys.exit(1)

    sync_file = resp.content.decode()
    return sync_file


def _check(instream):
    payload = json.load(instream)
    source = payload['source']
    token = source['github_token']
    repo = source['book_repo']
    server = source.get('archive_server')
    archive_server = determine_archive_server(server)

    msg("Syncing {} with {}...", repo, archive_server)

    sync_file = get_sync_file(token, repo)
    legacy_ids = parse_legacy_ids(sync_file)

    # Get versions from uuid via archive api
    versions = []
    for legacy_id in legacy_ids:
        try:
            uuid = BOOK_UUIDS[legacy_id]
        except KeyError as error:
            msg("Error: {}", error)
            sys.exit(1)
        link = f"https://{archive_server}/extras/{uuid}"
        resp = requests.get(link)

        if resp.status_code != 200:
            msg("Error: Unable to get version for {}", uuid)
            sys.exit(1)

        content = json.loads(resp.content)
        version = content['headVersion']
        versions.append(f'{legacy_id}@{version}')

    return [{"versions": ','.join(versions)}]


def main():
    print(json.dumps(_check(sys.stdin)))


if __name__ == '__main__':
    main()
