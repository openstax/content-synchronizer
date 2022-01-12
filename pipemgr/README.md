# Managing the syncing pipeline

## Always start by syncing your local osbooks list cleanly with what is on concourse.
> ### Notes about extracting:
> - Extracting resources will only add books to your local list that were not in it already
> - If you want to start from an empty book list, you can use the `clean` option
> - Unless you use the `clean` option, extracting will **never** remove books from your local list

```bash
# Enter the tool's parent directory
cd pipemgr

# Install dependencies if needed
poetry install --no-dev

# Sync your local osbooks list with what is on concourse
poetry run pipemgr extract --clean

# The clean option above ensures that any books that are not 
# in the pipeline will be removed from your local list

# List books
poetry run pipemgr list-books

# Add one or more books
# When adding books, the default server is cnx.org
poetry run pipemgr add-book osbooks-us-history --server qa
poetry run pipemgr add-book osbooks-college-physics

# Remove osbooks-us-history (server must match as well, default is cnx.org)
poetry run pipemgr remove-book osbooks-us-history --server qa

# Get a list of differences
poetry run pipemgr diff-books

# Get a list of differences and set the pipeline
poetry run pipemgr create

# Use poetry run pipemgr --help for more information about the command
```

# Running with Docker
All of the same commands apply; however, `pipemgr` is an installed package on the docker image. Consequently, you do not need to start each command with `poetry run` inside the docker container. 

## Volumes
If you want to keep your place, you should mount a volume over `/root/.pipemgr`

This will persist your oauth token and your osbooks list

## Here are helpful aliases that exist in the container
[Here](./env/.bashrc) are some useful aliases that you can use in the docker container.

# Running tests

This package generates a concourse pipeline using yaml template files. 

The testing suite adds and removes book resources, extracts books multiple times, and then checks if the generated pipeline is a valid concourse pipeline.

To run the tests, do the following: 
1. Run `poetry install` to install all dependencies
2. Run `poetry run pytest`
3. See results