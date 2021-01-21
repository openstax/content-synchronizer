# content-synchronizer
This repository holds scripts needed to synchronize content from archive to a github repository.

## Overview

Following steps can be run  manually to create a sync Docker image and update the repo:

```sh
docker build . -t git-storage-sync
docker run --rm -v $here:/output -e OUTPUT=/output -e GITHUB_TOKEN=$GITHUB_TOKEN -e BOOK_REPO_NAME=$BOOK_REPO_NAME git-storage-sync
```
`$here` Local location of script output, ideally the book repo you're trying to update
`$GITHUB_TOKEN` Personal Github Access Token
`$BOOK_REPO_NAME` Name of Github Book Repository

There are also unit tests for the sync scripts which can eventually be integrated with CI, but for the time being can be run manually:

```sh
pip install -r requirements.txt
pip install pytest pytest-mock
pytest test_sync_scripts.py
```
