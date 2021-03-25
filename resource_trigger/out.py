#!/usr/bin/env python3
import json
import sys

# This isn't doing anything


def _out(instream):
    payload = json.load(instream)

    return payload


def main():
    print(json.dumps(_out(sys.stdin)))


if __name__ == '__main__':
    main()
