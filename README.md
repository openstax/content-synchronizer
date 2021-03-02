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

To run the pipeline locally, populate the following in a `vars.yml` :
```
ce-dockerhub-id: dockerhubusername
ce-dockerhub-token: dockerhubpassword
ce-github-private-key: |
        -----BEGIN OPENSSH PRIVATE KEY-----
        ....
        -----END OPENSSH PRIVATE KEY-----
```

Then, set your pipeline with `vars.yml` containing your credentials.
and params: 
`osbook-git-uri`: git uri of book you want to sync
`sync-branch`: branch you want to sync
`from-server`: with which archive server
```
$ fly -t local-concourse set-pipeline -p sync-content -c sync.yml -l vars.yml -v osbook-git-uri=git@github.com:openstax/osbooks-college-algebra-bundle.git -v sync-branch=staging -v from-server=cnx.org
$ fly -t local-concourse unpause-pipeline -p sync-content
```