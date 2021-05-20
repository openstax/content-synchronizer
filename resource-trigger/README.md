# resource-trigger

This directory holds the resources to build the docker registry to trigger the sync pipline.

## How it Works

This resource uses the archive-api to check to see if a new version of content has been published.

The sync pipeline (`pipeline-sync.yml`) uses this resource as a trigger to start a sync job of pulling content from archive to update it's respective content repository.

## Development & Testing

Build Resource Image:
`docker build <docker-account/image-name> .`

Test Resource Image for pipeline:
`docker run -i <docker-account/image-name> /opt/resource/check < concourse_payload.json`

Push Resource Image:
`docker push <docker-account/image-name>`

Reference to pushed resource image in `pipeline-sync.yml`:

```
resource_types:
  - name: archive-api
    type: registry-image
    source:
      <<: *docker-credentials
      repository: openstax/sync-resource
      tag: main

resources:
  - name: version-checker
    type: archive-api
    source:
      archive_server: ((archive-server))
      book_repo: ((book-repo))
      github_token: ((github-api-token))
```

Set pipeline with:

```
fly -t local-concourse set-pipeline \
--config pipeline-sync.yml \
--load-vars-from vars.yml \
--pipeline sync-pipeline \
--var sync-branch=staging \
--var archive-server=qa.cnx.org \
--var book-repo=osbooks-college-algebra-bundle
```

Short hand

```
fly -t local-concourse sp -c pipeline-sync.yml -l vars.yml -p sync-pipeline -v sync-branch=staging-python -v archive-server=qa.cnx.org -v book-repo=osbooks-college-algebra-bundle
```

#### Helpful Debugs

```
fly -t local-concourse intercept -j sync-staging/sync-archive-staging-to-git-staging
fly -t local-concourse check-resource --
```
