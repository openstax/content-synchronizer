## First-time setup
Use either `poetry install` or `pip instal -r requirements.txt`. This document assumes you are using `poetry`.

## Managing the syncing pipeline

**Always start by syncing your local osbooks list with what is on concourse!**

- Notes about extracting:
    - Extracting resources will only add books to your local list that were not in it already
    - If you want to start from an empty book list, you can use the clean option

```bash
# Enter the tool's parent directory
cd pipemgr

# Perform first-time setup if you need to with `poetry install`

# Enter your virtualenv
poetry shell

# Sync your local osbooks list with what is on concourse
# Note: this assumes that you have your target named v7
fly -t v7 gp -p sync-osbooks | poetry run pipemgr extract

# List books
poetry run pipemgr list-books

# Add one or more books
# When adding books, the default server is cnx.org
poetry run pipemgr add-book osbooks-us-history --server qa
poetry run pipemgr add-book osbooks-college-physics

# Remove osbooks-us-history (server must match as well, default is cnx.org)
poetry run pipemgr remove-book osbooks-us-history --server qa

# Generate the pipeline file (outputs to ./sync-osbooks.yml by default)
poetry run pipemgr create

# Set the pipeline
fly -t v7 sp -p sync-osbooks -c sync-osbooks.yml

# Use poetry run pipemgr --help for more information about the command
```

---

## Running tests

This package generates a concourse pipeline using yaml template files. 

The testing suite adds and removes book resources, extracts books multiple times, and then checks if the generated pipeline is a valid concourse pipeline.

To run the tests: 
1. Make sure your environment is configured (see above)
2. Run `pytest`
3. Results