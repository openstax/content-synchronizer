#!/usr/bin/env python3
import json
import sys

# This isn't doing anything


def _out(instream):
    payload = json.load(instream)

    return payload


if __name__ == "__main__":
    print(json.dumps(_out(sys.stdin)))
