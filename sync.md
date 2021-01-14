# Overview

The sync scripts / code in this repo will eventually be moved into a dedicated repository once we're ready to start creating pipelines to automate this process. For the time being, the following steps can be run  manually to create a sync Docker image and udpate the repo:

```sh
docker build . -t git-storage-sync
docker run --rm -v $PWD:/output -e OUTPUT=/output git-storage-sync
```

There are also unit tests for the sync scripts which can eventually be integrated with CI, but for the time being can be run manually:

```sh
pip install -r requirements.txt
pip install pytest pytest-mock
pytest test_sync_scripts.py
```
