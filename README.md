# content-synchronizer

This repository holds scripts, images, and a pipeline configuration file used to sync book content from an **cnx archive server** to a **Github book repository**.

The content-synchronizer is a concourse pipeline (`pipeline-sync.yml`). Once a book repository is created and contains an *archive-syncfile* a pipeline can be set up (using the **Quick Start** steps below) to start the syncing process.

Once a book repository is ready to be updated/ edited using [POET](https://github.com/openstax/poet) syncing will cease.
## How it Works
Once a pipeline is set up - A pipeline gets triggered when a book is published, a new version of the book is detected. A job will start to pull the content from the specified archive server (`archive-server`) to the specified book repository branch (`sync-branch`).
## Quick Start
Note: Book repository must contain an `archive-syncfile`, example can be found on [osbooks-college-algebra-bundle](https://github.com/openstax/osbooks-college-algebra-bundle/) book repo.

### Use the Concourse `fly cli` to set up a pipeline to sync book repository.

```
fly -t opsx-concourse set-pipeline \
--config pipeline-sync.yml \
--pipeline sync-pipeline \
--load-vars-from vars.yml \
--var book-repo=osbooks-college-algebra-bundle \
--var archive-server=qa
```

Command Shorthand:
```
fly -t local-concourse sp -c pipeline-sync.yml -p sync-pipeline -l vars.yml -v book-repo=osbooks-college-algebra-bundle -v archive-server=qa
```

**Where..**
- `--config` - pipeline configuration file
- `--pipeline` - name of pipeline
- `--load-vars-from` - contains credentials / tokens for pipeline (`vars.yml` template)  

`vars.yml` template:
```
ce-dockerhub-id: <dockerhubusername>
ce-dockerhub-token: <dockerhubpassword>
github-token: <githubtoken>
ce-github-private-key: |

-----BEGIN OPENSSH PRIVATE KEY-----

........

-----END OPENSSH PRIVATE KEY-----
```

**.. and pipeline variables (`--var`):**
- book-repo - name of the Github book repository, content book repos are denoted with "osbooks" 
- archive-server - archive server the content will come from
- sync-branch - branch of the book repository to sync content to

## Development & Testing

### Sync Script
Following steps can be run manually to create a sync Docker image containing the `sync.sh` script and update the repo:

```sh
content-syncronizer$ docker build . -t git-storage-sync
content-syncronizer$ docker run --rm -v $PWD:/output -e OUTPUT=/output git-storage-sync /code/scripts/sync.sh
```

`$here` Local location of script output, ideally the book repo you're trying to update

There are also unit tests for the sync scripts which can eventually be integrated with CI, but for the time being can be run manually:

```sh
content-syncronizer$ pip install -r requirements.txt
content-syncronizer$ pip install pytest pytest-mock
content-syncronizer$ pytest test_sync_scripts.py
```