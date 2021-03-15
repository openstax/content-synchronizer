#!/usr/bin/env python3
import requests
import json
import sys

from utils import msg, parse_legacy_ids, determine_archive_server


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

    # Get uuid from legacy ids
    # BETTER: could reach into the db and generate this uuid.json
    legacy_ids = parse_legacy_ids(resp)
    with open("/opt/resource/uuids.json") as file:
        data = json.load(file)

    try:
        uuids = [data[legacy_id] for legacy_id in legacy_ids]
    except KeyError as error:
        msg(error, file=sys.stderr)
        sys.exit(1)

    # Get versions from uuid via archive api
    versions = ['']
    for uuid in uuids:
        link = f"https://{archive_server}/contents/{uuid}"
        resp = requests.get(link)

        if resp.status_code != 200:
            msg(f"Error: Unable to get version for {uuid}")
            sys.exit(1)

        content = json.loads(resp._content)
        version = content['version']
        versions.append(version)

    return [{"versions": 'v'.join(versions)}]


if __name__ == "__main__":
    print(json.dumps(_check(sys.stdin)))
