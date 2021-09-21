# resource-synchronizer

This directory holds the resources to build the docker registry to sync book content from an **cnx archive server** to a **Github book repository**.

## How it Works

This resource uses nebuchadnezzar to pull content from archive and sets the content to match the schema for the book repository.

The sync pipeline (`pipeline-sync.yml`) uses this resource as a way to retrieve updated content and to update the the respective content repository on Github.

## Development & Testing

### Sync Script

Following steps can be run manually to create a sync Docker image containing the `sync.sh` script and update the repo:

Options for selecting the input collections are either:
* an empty book repository based on [template-osbooks](https://github.com/openstax/template-osbooks) with `META-INF/books.xml` pointing to the collections.
* or a local file `./archive-syncfile` containing collections.

Example for `archive-syncfile` with "American Government" book:
```
american-government col11995
```

```sh
resource-synchronizer$ docker build . -t git-storage-sync
resource-synchronizer$ mkdir testrun
resource-synchronizer$ cd testrun
resource-synchronizer$ echo american-government col11995 >archive-syncfile
resource-synchronizer$ docker run --rm -v $PWD:/output -w /output -e SERVER=cnx.org git-storage-sync /code/scripts/sync.sh
# directory "testrun" should be now in GitHub format
```

`$here` Local location of script output, ideally the book repo you're trying to update

#### Tests

Run unit tests for the sync scripts, manually:

```sh
resource-synchronizer$ pip install -r requirements.txt
resource-synchronizer$ pip install pytest pytest-mock
resource-synchronizer$ pytest test_sync_scripts.py
```

#### Special case: Migrate neb format collections from local file structure into GitHub Format without using archive servers

Requirements are as before a [template-osbooks](https://github.com/openstax/template-osbooks) repo template with right `META-INF/books.xml` or an `archive-syncfile`.

The main difference is to move the local collections into the directories as defined in `META-INF/books.xml` or an `archive-syncfile` and **remove** the `neb` command from the process.

Instructions:
* Copy neb formatted files into directory structure as defined in `META-INF/books.xml` or an `archive-syncfile` (it is recommended to do a backup of the whole directory structure before running the sync command)
* Remove or comment out [this two lines](https://github.com/openstax/content-synchronizer/blob/725eae83dc7e11aac7f41b27e453940894593649/resource-synchronizer/sync.sh#L37-L38) of the script.
* (Re-)build the docker container: `docker build . -t git-storage-sync`
* Run the sync script as before in the neb formatted directory structure `docker run --rm -v $PWD:/output -w /output -e SERVER=cnx.org git-storage-sync /code/scripts/sync.sh`
* You now should have a GitHub formatted directory structure which only needs to be git pushed.