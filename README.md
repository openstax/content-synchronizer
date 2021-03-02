# content-synchronizer
This repository holds scripts needed to synchronize content from archive to a github repository.

## Overview

Following steps can be run  manually to create a sync Docker image and update the repo:

```sh
docker build . -t git-storage-sync
docker run --rm -v $here:/output -e OUTPUT=/output -e git-storage-sync
```
`$here` Local location of script output, ideally the book repo you're trying to update

There are also unit tests for the sync scripts which can eventually be integrated with CI, but for the time being can be run manually:

```sh
pip install -r requirements.txt
pip install pytest pytest-mock
pytest test_sync_scripts.py
```
## Development

To run the pipeline locally:
Populate the following in a `yml` :
```
ce-dockerhub-id: dockerhubusername
ce-dockerhub-token: dockerhubpassword
ce-github-private-key: |
        -----BEGIN OPENSSH PRIVATE KEY-----
        ....
        -----END OPENSSH PRIVATE KEY-----
```

Set your pipeline with `yml` containing your credentials.
```
fly -t local-concourse set-pipeline -p sync-branch -c sync_branch.yml -l credentials.yml
fly -t local-concourse unpause-pipeline -p sync-branch
```