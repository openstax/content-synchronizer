# content-synchronizer

This repository holds scripts, docker resources, and a pipeline configuration file used to sync book content from an **CNX Archive Server** to a **Github Book Repository**.

The content-synchronizer is a concourse pipeline (`pipeline-sync.yml`).

Once a book repository is created by a content manager and contains an _archive-syncfile_ or a _META-INF/books.xml_ a pipeline can be set up using the **_Quick Start_** steps below to start the syncing process.

Once a book repository is ready to be updated/ edited using [POET](https://github.com/openstax/poet) syncing will cease.

## How it Works

When a pipeline is set up (**_Quick Start_** steps) a job is triggered when a new version of the book is detected (by resource-trigger).

The job will (use the resource-synchronizer to):

- pull content from specified archive server
- set content to match the schema for book repository

then push to respective book repository's main branch.

## Quick Start

Note: Book repository must contain an `archive-syncfile` or a `META-INF/books.xml`, example can be found on [osbooks-college-algebra-bundle](https://github.com/openstax/osbooks-college-algebra-bundle/) book repo.

This document assumes you have the [fly cli](https://concourse-ci.org/fly.html) for Concourse and [fly targets](https://concourse-ci.org/fly.html#fly-login) set up with proper concourse-urls. See the [concourse tutorial](https://concoursetutorial.com/) for more information related to fly.

## Update the sync books pipeline
Checkout the instructions located in the [pipemgr](./pipemgr/README.md) directory for more information about managing the pipeline.

---

## Process for Existing Archive Books

Only pertains to books that exist in Archive and need to be moved to Github.

### To Sync

Step 1 - (CM) Start Process to Sync:

- Create the Github Content Repo:
  - Add License file
  - Add META-ING/books.xml
  - Set correct access permissions
  - Make Repository Private
- Create Github Issue Card for CE:
  - Title: Sync Content Repo: Repo-Name
  - Include:
    - Link to Github Content Repo
    - One Github Content Repo per Github Issue Card
    - Acceptance Criteria:
      - [Set up sync pipeline](https://github.com/openstax/content-synchronizer#quick-start)
      - Initial content sync is successful
      - Pipeline is linked in issue

Step 2 - (CE) Sync Content Repository:

- Complete Acceptance Criteria in Card
- "CE: Github Repo Stable Sync" with date / link to pipeline updated by Tester (Otto)

### To Unsync

Step 1 - (CM) Start Process to Unsync:

- Create Github Issue Card for CE:
  - Title: Unsync Content Repo: **Repo-Name**
  - Description:
    - Link to Github Content Repo
    - One Github Content Repo per Github Issue Card
    - Acceptance Criteria:
      - Remove book repository from sync pipeline
      - Announce in #books-and-candles that updates can be made in POET
      - Update Transition Plan Spreadsheet: Column "POET Editing Start Date"

Step 2 - (CE) Unsync Content Repository:

- Complete Acceptance Criteria in Card

---

## Process for New Book Repos

New books that do not exist in Archive, therefore no syncing needed, but will need minimum requirements for POET to work.

Step 1 (CM) - Create Seed Content Repository:

- Responsible Party: CMs
  - Create the Github Repo in Github
    - Add License file
    - Add META-ING/books.xml
    - Set correct access permissions
    - Make Repository Private
    - Add Vscode settings
    - Add Canonical.json
    - Add collections/collection.xml
    - Add media/<any_file>

* Note: We do not know if POET requires us to have `modules/` directory - case has not been tested yet.

---
## Releasing Changes and Updating Pipelines

From time to time we'll need to update the scripts or the dependencies. Anytime there is a merge on the main branch a GitHub workflow will tag an image with a timestamp and push it to Dockerhub. 

The following images are created from this repo:

* [openstax/content-synchronizer](https://hub.docker.com/repository/docker/openstax/content-synchronizer)
* [openstax/sync-resource](https://hub.docker.com/repository/docker/openstax/sync-resource)

When there is a change this tag needs to be added to the pipeline files and `fly set-pipeline` needs to be executed to update any of the sync pipelines if we want them to have the latest changes. 

---

## Resources:

- [Transition Plan](https://docs.google.com/spreadsheets/d/1qbkcpdpION-uN8GWW3zpanpunq4pjwqmVDGPOBhNW-8/edit#gid=0)
- [Minimum Requirement for POET (example repository)](https://github.com/philschatz/tiny-book)
- [First Issue for POET repos](https://github.com/openstax/cnx/issues/1462)

MISC NOTES:
Notables to answer - maybe:
While some books are in the phase of continuous syncing from archive, changes can be made to the repo that will require some migration. Give examples, these will be dealt as migration issues.
Migration: Restructure of book to take place - https://github.com/openstax/cnx/issues/1468
Note: Syncing overrides structure if not unsynced

Moves to POET only:
Ensure content version in repo (aka version last synced with archive) is correct
CM will start the unsyncing process
Steps:
Refer to issue - Manual removing of any leftover processing collation information “<?.....?>”, knowns:
Polish bundle, because wrong directory
Statistics High School, because `<!----` denoted before “<?...”
