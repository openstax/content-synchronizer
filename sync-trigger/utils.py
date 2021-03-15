import json
import sys
import re


def msg(msg, *args, **kwargs):
    if args or kwargs:
        msg = msg.format(*args, **kwargs)
    print(msg, file=sys.stderr)
    try:
        with open('/var/log/check', 'a') as f:
            f.write("msg:" + msg + "\n")
    except PermissionError:
        pass


def parse_legacy_ids(sync_file):
    sync_file = sync_file._content.decode()
    pattern = "col\\d{5}"
    legacy_ids = re.findall(pattern, sync_file)

    return legacy_ids


def determine_archive_server(server):
    if not server:
        msg("Error: No archive server was given.")
        sys.exit(1)
    delimiter = '-' if server.count('.') > 1 else '.'
    return 'archive' + delimiter + server
