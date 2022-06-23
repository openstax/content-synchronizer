#!/bin/bash
import json
import logging
import os
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

GITHUB_ENDPOINT = 'https://api.github.com/graphql'
GH_TOKEN = os.environ.get("GH_TOKEN")
ORGANIZATION = os.environ.get("GH_ORGANIZATION")
GH_API_ENDPOINT = os.environ.get("GH_API_ENDPOINT")
ABL_URL = os.environ.get("ABL_URL")


class GithubError(Exception):
    pass


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


REPOSITORY_QUERY = '''
query {
    organization(login: "openstax") {
        repositories(orderBy: { field: NAME, direction: ASC}
                     first: 100 %s) {
            nodes {
                name
            }
            pageInfo {
                endCursor
                hasNextPage
            }
        }
    }
}
'''


def load_abl():
    """This method loads the Approved Books List from the Openstax Github ABL endpoint"""
    try:
        req = Request(ABL_URL, method='GET')
        return json.loads(urlopen(req).read().decode('utf-8'))
    except Exception as e:
        print(e)
        raise GithubError(e)


def load_map():
    """This method loops through Openstax Github ABL books and matches collections ids and repositories."""
    approved_books = load_abl()['approved_books']
    print(f"Total ABL Books: {len(approved_books)}")
    map = {}
    for book in approved_books:
        if 'repository_name' in book:
            branches_url = f"{GH_API_ENDPOINT}/repos/openstax/{book['repository_name']}/branches"
            branches = json.loads(
                urlopen(Request(branches_url, method='GET', headers={'Authorization': 'token {}'.format(
                    GH_TOKEN)})).read().decode('utf-8'))
            for branch in branches:
                url = f"{GH_API_ENDPOINT}/repos/openstax/{book['repository_name']}/contents/META-INF/books.xml?ref={branch['name']}"
                try:
                    print(f"Querying URL: {url} ")
                    content = urlopen(Request(url, method='GET', headers={'accept': 'application/vnd.github.v3.raw',
                                                                          'Authorization': 'token {}'.format(
                                                                              GH_TOKEN)})).read().decode('utf-8')
                    for b in BeautifulSoup(content, 'lxml').find_all('book'):
                        if b.get('collection-id') and b.get('collection-id') not in map:
                            map[b.get('collection-id')] = {"collection_id": b.get("collection-id"),
                                                           "slug": b.get("slug"),
                                                           "repository_name": book['repository_name'],
                                                           "branch": branch['name']}
                except HTTPError as ex:
                    logging.exception(f"No book.xml found at {url}")
                    pass
    return map
