# resource-synchronizer

This directory holds the resources to build the docker registry to sync book content from an **cnx archive server** to a **Github book repository**.

## How it Works

This resource uses nebuchadnezzar to pull content from archive and sets the content to match the schema for the book repository.

The sync pipeline (`pipeline-sync.yml`) uses this resource as a way to retrieve updated content and to update the the respective content repository on Github.

## Development & Testing

### Sync Script

Following steps can be run manually to create a sync Docker image containing the `sync.sh` script and update the repo:

```sh
resource-synchronizer$ docker build . -t git-storage-sync
resource-synchronizer$ docker run --rm -v $PWD:/output -w /output -e SERVER=cnx.org git-storage-sync /code/scripts/sync.sh
```

`$here` Local location of script output, ideally the book repo you're trying to update

Run unit tests for the sync scripts, manually:

```sh
resource-synchronizer$ pip install -r requirements.txt
resource-synchronizer$ pip install pytest pytest-mock
resource-synchronizer$ pytest test_sync_scripts.py
```
