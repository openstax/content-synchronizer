#Migrating  CNX Archive books to Github

This project contains python scripts to query the CNX Archive database and generate json files that can be inputs for Concourse pipelines that will run the [Sync Script](../resource-synchronizer/sync.sh) for the migration.

## Python Scripts
#### [DB Connector](./db_connector.py)
This script is uses `psycopg2` to establish a connection to the Postgres DB
#### [Github Synchronizer](./github_synchronizer.py)
This scripts loads the ABL and generates a map that matches collection IDs and Github repositories and branches
#### [Query Books](./query_books.py)
This script queries books from the CNX  Database, Generates  [JSON files](./data/json) as output and updates this [html file](./data/index.html) for a more readable presentation.

## [Pipelines](./pipelines)
There are 3 different pipelines that vary based on the type of books we want to migrate.

> ###Pipelines Parameters
> All the pipelines requires the new Github account details such as:
> `var_sources[0].config.vars.username`: Destination Github account Username 
> `var_sources[0].config.vars.token`: Destination Github account Password
> `var_sources[0].config.vars.email`: Destination Github account email
> 
> The [Openstax Derived Books Pipeline](./pipelines/openstax_derived_books_pipeline.yml) requires:
> `var_sources[0].config.vars.openstax.username`: A Github account username that can access OpenStax private books repos and clone them
> `var_sources[0].config.vars.openstax.token`: Token for the Github account with private repositories privileges.




###[OpenStax Derived Books](./pipelines/openstax_derived_books_pipeline.yml)
This  pipeline takes the raw URL of the [openstax_derived_books.json](./data/json/openstax_derived_books.json), queues out the items in the json and pass them as input to the [sync script](../resource-synchronizer/sync.sh) for the migration.

###[Vendors Books](./pipelines/vendor_books_pipeline.yml)
This  pipeline takes the raw URL of the [vendors_books.json](./data/json/vendors_books.json), queues out the items in the json and pass them as input to the [sync script](../resource-synchronizer/sync.sh) for the migration.

###[Vendors Derived Books](./pipelines/vendor_derived_books_pipeline.yml)
This  pipeline takes the raw URL of the [vendors_derived_books.json](./data/json/vendors_derived_books.json), queues out the items in the json and pass them as input to the [sync script](../resource-synchronizer/sync.sh) for the migration.


###TODO
- [ ] Update Sync Script to push all branches to new repository
- [ ] Return a Slack Message when a pipeline job fails or succeeds.
